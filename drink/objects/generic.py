from __future__ import absolute_import, with_statement
import os
from urllib import quote, unquote
from datetime import datetime
from mimetypes import guess_type
import drink
from drink import request
from threading import Lock
from drink.types import dt2str
import bottle
import logging
log = logging.getLogger('obj')

__all__ = ['Page', 'ListPage', 'WebFile', 'Settings']

# TODO: Create a "BigListPage" (aka BigFolder) inheriting OOBtree & Page

class _Mock(object): pass

def get_type(filename):
    return guess_type(filename)[0] or 'application/octet-stream'

def get_struct_from_obj(obj, childs=None, full=None):

    if full is None:
        full = bool(request.params.get('full', childs or '').lower() != 'no')

    if childs is None:
        childs = bool(request.params.get('childs', '').lower() != 'no')

    a = request.identity.access

    d = dict()
    auth = a(obj)

    if 'r' in auth:
        d['id'] = quote(obj.id.encode('utf-8'))
        #d['logged_in'] = request.identity.success
        d['path'] = quote(obj.rootpath.encode('utf-8'))
        d['_perm'] = auth

        _fields = set(obj.editable_fields.keys())
        _child_fields = set(('title', 'description', 'default_action', 'mime'))
        _fields.update(_child_fields)

        def _getset(k):
            v = getattr(obj, k, None)
            if isinstance(v, (basestring, int, float)):
                pass # serializes well in json
            elif isinstance(v, drink.Model):
                if not 'r' in a(v):
                    return
                v = v.struct(False)
                if k != v['id']:
                    log.error('children ID not consistant with parent (%r != %r) !', k, v['id'])
            elif isinstance(v, datetime):
                v = dt2str(v)
            else:
                v = "N/A"
            d[k] = v

        for k in _fields:
            _getset(k)

        if full:
            for k in _child_fields:
                _getset(k)

            d['i_like'] = request.identity.id in obj._like if obj._like else False

            try:
                d['score'] = len(obj._like) - len(obj._unlike)
            except TypeError:
                d['score'] = 0

            d['actions'] = obj._actions
            d['loaders'] = obj.loaders

        if childs:
            items = []
            for v in obj.itervalues():
                c = v.struct(childs=False, full=False)
                if c:
                    items.append(c)
            d['items'] = items
            d['items_factory'] = obj.items_factory
            d['classes'] = obj.classes.keys()
        else:
            d['_nb_items'] = len(obj)

    return d


def default_view(self, page='main.html', obj=None, css=None, js=None, html=None, embed=None, classes=None, no_auth=None, **kw):
    """ Renders the :class:`~drink.Page` as HTML using a template

    :arg self: the object to render, should contain the following properties:

        :css: either a list of css http paths (str) or css block
        :js: either a list of javascript files (str) or javascript code
        :html: any html <body> content
        :classes: in case the `classes` parameter is not given

        .. note:: Additional properties may be required, depending on the template used (default is "main.html")

    :type self: any `object`

    :arg page: (defaults to "main.html") template to use for rendering
    :type page: a :func:`bottle.template` compatible template

    :arg obj: (optional) overrides `self` for `obj` template parameter. The access checking & so will use `self`.

    The following `self` attributes may be overriden:

    :arg css: The list of css files to use (http relative path) or the content itself
    :type css: `list` of `str` or `str` with newline(s)
    :arg js: The list of js files to use (http relative path) or the content itself
    :type js: `list` of `str` or `str` with newline(s)
    :arg html: HTML content of the `<body>` element
    :type html: `unicode`
    :arg classes: A mapping of ``{'Object name': Drink_Page_class}`` usable objects
    :type classes: `dict` of `str` : :class:`drink.Page`

    """
    if not no_auth and 'r' not in request.identity.access(self):
        return drink.unauthorized()

    drink.response.content_type = "text/html; charset=utf-8"

    if request.is_ajax:
        return {'html': html or self.html,
            'js': js or self.js,
            'css': css or self.css,
            }

    return bottle.template(page,
            template_adapter=bottle.Jinja2Template,
            obj=obj or self,
            css=css or self.css,
            js=js or self.js,
            html=html or self.html,
            embed=bool(drink.request.params.get('embedded', False)) if embed is None else embed,
            classes=self.classes if classes is None else classes,
            isattr=lambda x, name: hasattr(x, name),
            isstring=lambda x: isinstance(x, basestring),
            req=request,
            authenticated=request.identity,
            **kw
        )


class Page(drink.Model):
    """ A dict-like object, defining all properties required by a standard page """

    loaders = {
        'gallery': "$('#pikame').PikaChoose({transition:[0], showTooltips: true})",
        'view': "",
        'list': "var l=$('#main_list'); drink.entries.forEach( function(e) {l.append(e.elt) })",
        'edit': "",
    }

    #: fields that are editable (appear in edit panel)

    editable_fields = {
        'title': drink.types.Text('Title'),
        'description': drink.types.Text('Description'),
    }


    """
    def _p_resolveConflict(self, oldState, savedState, newState):

        # Figure out how each state is different:
        savedDiff= savedState['count'] - oldState['count']
        newDiff= newState['count']- oldState['count']

        # Apply both sets of changes to old state:
        return oldState['count'] + savedDiff + newDiff
"""

    #: fields that are only editable by the owner (appear in edit panel)

    owner_fields = {
        'default_action':
            drink.types.Text("Default action (ex: view, list, edit, ...)", group="w"),
        'easy_permissions':
            drink.types.EasyPermissions("EZ !", group="x_permissiona"),
        'allow_comments':
            drink.types.Text("Allow rating and posting comments (either nothing for no comments or a permission string)", group="comments"),
        'read_groups':
            drink.types.GroupCheckBoxes("Users allowed to view the document", group="starts_hidden x_permissions"),
        'min_rights':
            drink.types.Text("Every user's permissions (<strong>r</strong>ead, <strong>w</strong>rite, <big>t</big>raverse, <strong>a</strong>dd)", group="starts_hidden x_permissions"),
        'write_groups':
            drink.types.GroupCheckBoxes("Users allowed to edit the document", group="starts_hidden x_permissions"),
    }


    def serialize(self, recurse=True):
        d = {'drink__class': self.__class__.__name__}
        for field in self.owner_fields.keys() + self.admin_fields.keys() + self.editable_fields.keys():
            try:
                v = getattr(self, field)
                if isinstance(v, set):
                    v = list(v)

                d[field] = v
            except AttributeError:
                pass

        if recurse:
            c = d['drink__children'] = []
            for child in self.keys():
                c.append((child, self[child].serialize()))
        return d

    #: actions
    _actions = [
        dict(title="Help", action="/pages/help/", perm="r", icon="help"),
        dict(title="Back", action="ui.go_back()", perm="r", icon="undo"),
        dict(title="View/Reload", action="drink.serve(undefined, 'view')", icon="view", perm='r'),
        dict(title="Edit", style="edit_form", action="drink.serve(undefined, 'edit')", icon="edit", perm='w'),
        dict(title="List content", action="drink.serve(undefined, 'list')", icon="open", perm='r'),
        dict(title="Add object", condition="drink.d.classes.length!=0", style="add_form", action="ui.add_entry()", key='INS', icon="new", perm='a'),
        dict(title="Move", style="move_form", action="ui.move_current_page()", icon="move", perm='o'),
        dict(title="Image gallery", style="move_form", action="drink.serve(undefined, 'gallery')", icon="view", perm='r', key='G'),
    ]

    #: fields that are only editable by the admin (appear in edit panel)

    admin_fields = {}

    #: permissions to apply for comments (permissions required, nothing to disable comments & rating)
    allow_comments = ''

    #: permissions given to any user (anonymous or not)
    min_rights = 't'

    #: mime-type of the object, used for icon
    mime = 'page'
    #: list of css files required by this object
    css = []
    #: html content, used by default in :meth:`view`
    html = ''
    #: list of javascript files included in the views
    js = []
    #: short description of the object or instance
    description = u'An abstract page'

    #: dictionnary of ``{object_name: classe}``  allowed in that context
    classes = drink.classes

    #: default action if none specified
    default_action = "view"

    #: Is that type of object only accessible by admin ?
    hidden_class = False

    #: map used for upload action, to bind extensions to factories
    upload_map = {
        '*': 'WebFile',
    }

    # Model methods

    def _lock(self):
        if not getattr(self, '_v_lock', None):
            self._v_lock = Lock()
        return self._v_lock

    def __init__(self, name, rootpath=None):
        drink.Model.__init__(self)
        self.data = {}
        self.read_groups = set()
        self.write_groups = set()

        if not isinstance(name, basestring):
            # Root object special case, will pass the dict or None...
            if name is not None:
                self.data.update(name)
            name = u'/'
            #: Unique id
            self.id = u'.'
        else:
            if not name or name[0] in r'/.$%_':
                return drink.unauthorized('Wrong identifier: %r'%name)
            # minor sanity check
            self.id = name.replace(u' ', u'-').replace(u'\t', u'_').replace(u'/', u'.').replace(u'?', u'')

        self.rootpath = rootpath

        if not hasattr(self, 'title'):
            self.title = name.replace(u'_', u' ').replace(u'-', u' ').capitalize()

        try:
            self.owner
        except AttributeError:
            self.owner = request.identity.user

    def __hash__(self):
        return hash(self.id)

    @property
    def indexable(self):
        if isinstance(self.description, unicode):
            return self.description
        else:
            return self.description.decode('utf-8')

    @property
    def quoted_path(self):
        return quote(self.path.encode('utf-8'))

    @property
    def quoted_id(self):
        return quote(self.id.encode('utf-8'))

    def view(self, *a, **k):
        """ See :func:`default_view` """
        return default_view(self, *a, **k)

    #: A map of <html/js event>: <js function>, used to hook items interactions

    items_factory = {
            # TODO: make it really generic, not just look-a-like
        'dblclick': "edit_title",
        'hover': "popup_actions",
        'entry': "default_factory",
    }

    def struct(self, childs=None, full=None):
        """ returns this item as a json structure """
        return get_struct_from_obj(self, childs, full)

    _like = None
    _unlike = None

    def rate(self):
        rate = 0
        if request.params.get('like'):
            rate += 1
        if request.params.get('unlike'):
            rate -= 1

        if rate != 0:
            if self._like is None:
                self._like = set()
            if self._unlike is None:
                self._unlike = set()

            if rate > 0:
                self._like.add(request.identity.id)
                self._unlike.discard(request.identity.id)
            else:
                self._unlike.add(request.identity.id)
                self._like.discard(request.identity.id)
            drink.transaction.commit()

        plus = len(self._like) if self._like else 0
        minus = len(self._unlike) if self._unlike else 0
        return {'rating': plus - minus, 'redirect': self.path}

    _comments = None

    def comment(self):
        txt = drink.omni(request.params.get('text', ''))
        if txt:
            if not self._comments:
                self._comments = []
            self._comments.append( {'from': request.identity.id, 'message': txt} )
            drink.transaction.commit()
        return {'comments': self._comments or [], 'redirect': self.path}

    @property
    def path(self):
        """ Item's relative HTTP path """
        return self.rootpath + self.id + u'/'

    def set_field(self, name, val):
        """ Set the field *name* to value *val*

        :arg name: name of the :data:`~drink.Page.editable_fields` to set
        :type name: str

        :arg val: value of the field
        :type val: depends on the :mod:`~drink.types`
        """
        if name in self.editable_fields:
            if 'w' in drink.request.access(self):
                self.editable_fields[name].set(self, name, val)
            else:
                return drink.unauthorized("You can't edit %r, ask for more permissions."%name)
        elif name in self.owner_fields:
            if 'o' in drink.request.access(self):
                self.owner_fields[name].set(self, name, val)
            else:
                return drink.unauthorized("You can't edit %r, ask for more permissions."%name)
        else:
            return drink.unauthorized("%r is not editable."%name)

    def get_field(self, name):
        """ Get the value of field *name*

        :arg name: name of the :data:`~drink.Page.editable_fields` to set
        :type name: str
        :returns: The associated value

        .. todo:: add types's internal representation doc + link to it
        """
        return self.editable_fields[name].get(self, name)

    def edit(self, resume=None):
        """ Edit form

        :arg resume: when given, won't call :meth:`~drink.Page._edit` but use this return value instead
        :type resume: bool
        :returns: a form allowing to edit the object or http error

        call :meth:`~drink.Page._edit` method and return it's value.
        In case you return a tuple which first parameter is callable,
        then it calls the callable with the other tuple elements as parameters.
        This is used to handle redirects, from "inside" you should always use :meth:`~drink.Page._edit` !

        """
        with self._lock():
            r = resume or self._edit()
            drink.transaction.commit() # commit before eventual redirect
        return r

    def _update_lookup_engine(self, add=False, remove=False):
        database = drink.db.db
        if 'search' in database:
            if add:
                database['search']._add_object(self)
            elif remove:
                database['search']._del_object(self)
            else:
                database['search']._update_object(self)

    def _edit(self):
        """ Implementation of public :meth:`~drink.Page.edit` method,
        only looks at http environment for now (no useable parameter).

        .. note::  Use :meth:`.set_field` to set some editable field value.

        Use :

        .. rubric:: HTTP parameters (other that the properties' names)

        :_dk_fields: Field names to edit, separated by a slash ``/``
        :embedded: Just transmits this parameter to next page
        :_recurse: Special mode applying permissions (only) in a recursive way

        """

        if 'w' not in request.identity.access(self):
            return drink.unauthorized()

        items = self.editable_fields.items()
        if request.identity.id == self.owner.id or request.identity.admin:
            items += self.owner_fields.items()

        if request.identity.admin:
            items += self.admin_fields.items()

        forms = request.forms
        embedded = bool(request.params.get('embedded', ''))
        recursive = bool(request.params.get('_recurse', ''))

        if forms:
            if '_dk_fields' in forms:
                editable = forms.get('_dk_fields').split('/')
            else:
                editable = forms.keys()

            files = request.files.keys()

            for attr, caster in items:
                if attr in files:
                    caster.set(self, attr, request.files.get(attr))
                elif attr in editable:
                    v = forms.get(attr)
                    caster.set(self, attr, v.decode('utf-8') if v else u'')

            self._update_lookup_engine()
            if recursive:
                # apply permissions recursively
                childs = list(self.values())
                for child in childs:
                    try:
                        child.read_groups = self.read_groups
                        child.write_groups = self.write_groups
                    except Exception, e:
                        log.warning('error applying permissionson %r : %r', child, e)
                    else:
                        childs.extend(child.values())
            return {'redirect': "%s?embedded=%s"%(self.quoted_path, '1' if embedded else '' )}
        else:
            if not items:
                form = ['<div class="error_message">Not editable, sorry...</div>']
            else:
                # sort by group+id
                items.sort(key=lambda o: o[1].group.split()[-1]+o[0])
                current_group = None
                form_opts = []
                form = ['<input type="hidden" name="_dk_fields" value="%s" />'%('/'.join(x[0] for x in items))]
                if embedded:
                    form.append('<input type="hidden" name="embedded" value="1" />')
                for field, factory in items:
                    if factory.form_attr:
                        form_opts.append(factory.form_attr)
                    if factory.group != current_group:
                        old_group = current_group
                        current_group = factory.group
                        if old_group:
                            form.append('</div>')
                        form.append('<div class="%s_grp">'%current_group)
                    val = getattr(self, field, '')
                    form.append('<li class="entry"><div class="input">%s</div></li>'%factory.html(field, val))
                form.append('''</li></div></ul>
                <input class="submit" type="submit" value="Save changes please"/>
                </form>''')
                form.insert(0, '''<form
                 class="auto_edit_form" id="auto_edit_form" action="edit" %s method="post"><ul class="editable_fields">'''%(' '.join(form_opts)))
            return drink.default_view(self, html='\n'.join(form))

    def _upload(self, obj):
        self.editable_fields['content'].set(self, 'content', obj)

    def upload(self):
        if 'w' not in request.identity.access(self):
            return drink.unauthorized()

        try:
            filename = request.GET.get('qqfile', '').decode('utf-8')
        except UnicodeError:
            filename = request.GET['qqfile'].decode('latin1')
        if not filename:
            return {'error': True, 'code': 400, 'message': 'Incorrect parameters. Action aborted.'}

        factory = self.upload_map.get(filename.rsplit('.')[-1], 'WebFile')

        with self._lock():

            o = self._add(filename, factory,
                request.identity.user.default_read_groups,
                request.identity.user.default_write_groups)
            o.mimetype = get_type(filename)

            fake_post_obj = _Mock()

            fake_post_obj.file = request.body
            fake_post_obj.filename = filename

            o._upload(fake_post_obj)

            data = o.struct()
            data['success'] = True

        return data

    def rm(self):
        # TODO: ajaxify
        name = drink.omni(request.GET.get('name'))
        if not ('a' in request.identity.access(self) and 'w' in request.identity.access(self[name])):
            return drink.unauthorized("Not authorized")
        try:
            parent_path = self.quoted_path
        except AttributeError: # XXX: unclean
            parent_path = '.'

        with self._lock():
            old_obj = self[name]
            del self[name]
            old_obj._update_lookup_engine(remove=True)
            drink.transaction.commit()

        return drink.rdr(parent_path)

    def _match(self, pattern=None):
        if pattern is None:
            pattern = ''
        return {'items': [k for k in self.iterkeys() if pattern in k]}

    def match(self, pattern=None):
        if 'r' not in request.identity.access(self):
            return drink.unauthorized()

        return self._match(pattern or request.params.get('pattern').decode('utf-8') )

    def _add(self, name, cls, read_groups, write_groups):
        if isinstance(cls, basestring):
            klass = self.classes[cls] if self.classes else drink.classes[cls]
        else:
            klass = cls
        if klass.hidden_class and not request.identity.admin:
            return None
        new_obj = klass(name, self.path)
        if not new_obj.read_groups:
            new_obj.read_groups = set(read_groups)
        if not new_obj.write_groups:
            new_obj.write_groups = set(write_groups)

        self[new_obj.id] = new_obj
        new_obj._update_lookup_engine(add=True)
        drink.transaction.commit()
        return new_obj

    def add(self, name=None, cls=None, read_groups=None, write_groups=None):
        auth = request.identity

        if 'a' not in auth.access(self):
            return drink.unauthorized("Not authorized")

        name = name or request.params.get('name').decode('utf-8')

        if name in self:
            return drink.unauthorized("%r is already defined!")

        if None == cls:
            cls = request.params.get('class')
        if not cls:
            return drink.unauthorized("%r incorrect request!"%name)

        with self._lock():
            o = self._add(name, cls, auth.user.default_read_groups, auth.user.default_write_groups)
        if o is None:
            return drink.unauthorized("You can't create %r objects!"%name)

        if request.is_ajax:
            return o.struct()
        else:
            return drink.rdr(o.quoted_path+'edit')

    def borrow(self, item=None):
        """ Borrow an external item """
        if not item:
            item = drink.get_object(drink.db.db, request.POST['item'])
        if item.id in self:
            return drink.unauthorized("An object with the same id stands here!")
        if self.path in item.path:
            return drink.unauthorized("Can't move an object to one if it's children!")
        try:
            parent = drink.get_object(drink.db.db, item.rootpath)
        except Exception, e:
            return drink.unauthorized("Unhandled error: %r"%e)
        finally:
            item._update_lookup_engine(remove=True)
            self[item.id] = item
            del parent[item.id]
            item._update_lookup_engine(add=True)
            item.rootpath = self.path

        return {'success': True}

    def list(self):
        return drink.default_view(self, 'main.html', html=u'<h1>%s</h1>\n<ul id="main_list" class="sortable" />'%self.title)

    def gallery(self):
        def _g():
            for i in self.itervalues():
                if getattr(i, 'mimetype', '').startswith('image'):
                    try:
                        yield '<li><a href="%s"><img title="%s" src="%sraw" /></a><span>%s</span></li>'%(i.path, i.title,  i.path, i.description)
                    except Exception, e:
                        log.error('Image error: %r', e)

        html = '''<div><ul id="pikame">
        %s
        </ul>

        <script>
        // Load the classic theme

        </script>
        </div>
        '''%'\n'.join(_g())

        return default_view(self, html=html, js=self.js+["/static/js/jquery.pikachoose.js"], css=self.css+["/static/css/pikachoose.css"])


class ListPage(Page):

    drink_name = "Folder index"

    description = u"An ordered folder-like display"

    default_action = 'list'

    mime = "folder"

    forced_order = None

    _actions = Page._actions + [dict(perm='w', title="Reset items", action="$.ajax({url:base_path+'reset_items'}).success(function(){drink.cur_action=null; drink.serve())", icon="download")]

    def __init__(self, name, rootpath=None):
        self.forced_order = []
        Page.__init__(self, name, rootpath)
        if 0 != len(self):
            self.forced_order = self.data.keys()

    def iterkeys(self):
        return iter(self.forced_order)
        #k = Page.keys(self)
        #return (x for x in self.forced_order if x in k) or k

    def keys(self):
        return list(self.forced_order)

    def move(self):
        if 'w' not in request.identity.access(self):
            return drink.unauthorized()

        if request.is_ajax:
            self.forced_order = unquote(request.params.get('set')).decode('utf-8').split('/')
        else:
            html = '<input type="text" class="completable" complete_type="objpath" value="/pages/"></input>'
            return self.view(html=html)

    def itervalues(self):
        for k in self.iterkeys():
            try:
                yield self[k]
            except KeyError:
                log.error("Err, no such key: %r", k)

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        for k in self.iterkeys():
            yield (k, self[k])

    def items(self):
        return list(self.iteritems())

    def reset_items(self):
        if 'o' not in request.identity.access(self):
            return drink.unauthorized("You must be the owner to do that")

        orig_order = []
        k = set(Page.keys(self))

        for item in self.forced_order:
            if item not in orig_order and item in k:
                orig_order.append(item)
        unlisted = k.difference(orig_order)
        orig_order.extend(unlisted)
        self.forced_order = orig_order
        return {'success': True}

    def __setitem__(self, name, val):
        try:
            r = Page.__setitem__(self, name, val)
        except Exception:
            raise
        else:
            self.forced_order.append(name)
            return r

    def __delitem__(self, name):
        try:
            r = Page.__delitem__(self, name)
        except Exception:
            raise
        else:
            self.forced_order.remove(name)
            return r


class WebFile(Page):

    drink_name = "WebFile"
    mime = "page"
    mimetype = "text/plain"
    description = u"Some file"
    classes = {}

    owner_fields = Page.owner_fields.copy()
    owner_fields.pop('default_action')
    owner_fields['mime'] = drink.types.Mime()

    editable_fields = Page.editable_fields.copy()

    editable_fields.update( {
        'content':
            drink.types.File("File to upload"),
#        'content_name': drink.types.Text("File name"),
        'mimetype': drink.types.Text("mimetype (rendering)"),
    } )

    content = ''
    content_name = "unnamed"

    @property
    def indexable(self):
        if isinstance(self.description, unicode):
            desc = self.description
        else:
            desc = self.description.decode('utf-8')
        if isinstance(self.content, unicode):
            cont = self.description
        else:
            cont = u''
        return u'%s\n%s'%(desc, cont)

    def serialize(self, recurse=False):
        if 'o' not in request.identity.access(self):
            return drink.unauthorized("You must be the owner to do that")

        d = Page.serialize(self, recurse=False)
        d['drink__filename'].self.content.filename
        return d

    def raw(self):
        if 'r' not in request.identity.access(self):
            return drink.unauthorized()
        try:
            if self.content:
                root, fname = os.path.split(self.content.filename)
                return drink.static_file(fname, root, mimetype=self.mimetype, download=self.content_name)
        except Exception, e:
            log.error('Error while handling %r', self.path)

        #Alternatively: drink.response.headers['Content-Type'] = '...'
        # + read

    def _edit(self):
        # In case the user didn't change the mimetype
        # we guess it from the uploaded file name

        old_mimetype = self.mimetype
        r = Page._edit(self)
        if old_mimetype == self.mimetype \
           and request.forms.keys() and 'content' in request.files \
           and request.files['content'].filename:
            self.mimetype = get_type(self.content_name)
        return r

    @property
    def html(self):
        if 'r' not in request.identity.access(self):
            return drink.unauthorized()

        drink.response.content_type = "text/html; charset=utf-8"
        r = []
        if self.content:
            mime = self.mimetype
            try:
                sz = os.stat(self.content.filename).st_size
            except Exception, e:
                log.error(repr(e))
                sz = 0
            if not sz:
                r.append(u'<h1>No content :(</h1>')
            else:
                r.append(u'<h1 title="%s">%s<a href="raw"><img src="/static/actions/download.png" title="Click here to download (%sB)"/></a></h1>'%(self.description, self.content_name, drink.bytes2human(sz)))
                r.append(u'<div class="contents">')
                if mime.startswith('image/'):
                    r.append(u'<img src="raw" style="width: 80%; margin-left: 10%; margin-right: 10%;"/>')
                elif mime in ('application/xml', ) or mime.startswith('text/'):
                    f = self.content.open('r')
                    r.append(u'<pre>')
                    r.append(unicode(f.read(), 'utf-8'))
                    r.append(u'</pre>')
                r.append(u"</div>")
        else:
            r.append(u'<h1>No content :(</h1>')

        return u''.join(r)


class Settings(Page):
    description = 'Drink settings panel'
    default_action = 'edit'
    classes = {}
    server_backend = 'auto'
    server_port = 5000
    server_address = '0.0.0.0'
    debug_framework = 'auto'
    active_objects = set('generic users tasks markdown finder filesystem sonic'.split())

    owner_fields = {}

    editable_fields = {
        'server_backend': drink.types.Choice('WSGI server', group='server', options={
            'Paste': 'paste',
            'Bjoern': 'bjoern',
            'Gevent': 'gevent',
            'Debug mode': 'debug',
            'Automatic': 'drink',
            }),
        'server_port': drink.types.Int('HTTP port', group='server_addr2'),
        'server_address': drink.types.Text('Server address', group='server_addr1'),
        'debug_framework': drink.types.Choice('Debug framework', group='debug', options={
            'Weberror middleware': 'weberror',
            'werkzeug.debug': 'werkzeug',
            'repoze.debug': 'repoze',
            'Automatic': 'auto',
            }),
        'active_objects': drink.types.CheckboxSet('Enabled modules', group='plugins', options=active_objects),
    }
