from __future__ import absolute_import
import os
from datetime import datetime
from mimetypes import guess_type
import transaction
import drink
from drink import request
from drink import template
from drink.types import dt2str
from drink.zdb import Model
from . import classes

# TODO: Create a "BigListPage" (aka BigFolder) inheriting OOBtree & Page

class _Mock(object): pass

def get_type(filename):
    return guess_type(filename)[0] or 'application/octet-stream'

def get_struct_from_obj(obj, childs, full):
    k = request.params.keys()
    if None == full:
        full = 'full' in k

    if 'childs' in k:
        childs = request.params['childs'].lower() in ('yes', 'true')

    a = request.identity.access

    d = dict()
    auth = a(obj)

    if 'r' in auth:
        d['id'] = obj.id
        d['title'] = obj.title
        d['description'] = obj.description
        d['path'] = obj.rootpath
        d['mime'] = obj.mime
        d['_perm'] = auth

        if full:
            for k in obj.editable_fields.keys():
                if k in d:
                    continue
                v = getattr(obj, k, None)
                if isinstance(v, Model):
                    if not 'r' in a(v):
                        continue
                    v = v.struct(False)
                    v['id'] = k
                elif isinstance(v, (basestring, int, float)):
                    pass # serializes well in json
                elif isinstance(v, datetime):
                    v = dt2str(v)
                else:
                    v = "N/A"
                d[k] = v

        if childs:
            items = []
            for v in obj.itervalues():
                auth = a(v)
                if 'r' in auth:
                    c = v.struct(childs=False)
                    c['_perm'] = auth
                    items.append(c)
            d['items'] = items
        else:
            d['_nb_items'] = len(obj)

    return d

class Page(Model):
    """ A dict-like object, defining all properties required by a standard page """

    #: fields that are editable (appear in edit panel)

    editable_fields = {
        'title': drink.types.Text('Title'),
        'description': drink.types.Text('Description'),
    }

    #: fields that are only editable by the owner (appear in edit panel)

    owner_fields = {
        'default_action':
            drink.types.Text("Default action (ex: view, list, edit, ...)", group="w"),
        'easy_permissions':
            drink.types.EasyPermissions("EZ !", group="x_permissiona"),
        'read_groups':
            drink.types.GroupCheckBoxes("Read-enabled groups", group="x_permissions"),
        'min_rights':
            drink.types.Text("Every user's permissions (wrta)", group="x_permissions"),
        'write_groups':
            drink.types.GroupCheckBoxes("Write-enabled groups", group="x_permissions"),
        'disable_ajax' :
            drink.types.BoolOption('Disable Js')
    }

    #: fields that are only editable by the admin (appear in edit panel)

    admin_fields = {}

    #: permissions given to any user (anonymous or not)
    min_rights = ''

    #: mime-type of the object, used for icon
    mime = 'page'
    #: object may read this to disable some ajax
    disable_ajax = False
    #: list of css files required by this object
    css = []
    #: html content, used by default in :meth:`view`
    html = ''
    #: list of javascript files included in the views
    js = []
    #: short description of the object or instance
    description = 'An abstract page'
    #: dictionnary of classes allowed in that contect
    classes = drink.classes

    #: default action if none specified
    default_action = "view"

    #: map used for upload action, to bind extensions to factories
    upload_map = {
        '*': 'WebFile',
    }

    # Model methods

    def __init__(self, name, rootpath=None):
        Model.__init__(self)
        self.data = {}
        self.read_groups = set()
        self.write_groups = set()

        if not isinstance(name, basestring):
            # Root object special case, will pass the dict or None...
            if name is not None:
                self.data.update(name)
            name = '/'
            self.id = '.'
        else:
            if not name or name[0] in r'/.$%_':
                drink.unauthorized('Wrong identifier: %r'%name)
            # minor sanity check
            self.id = name.replace(' ', '-').replace('\t','_').replace('/','.').replace('?', '')

        self.rootpath = rootpath

        if not hasattr(self, 'title'):
            self.title = name.replace('_', ' ').replace('-', ' ').capitalize()

        try:
            self.owner
        except AttributeError:
            self.owner = request.identity.user

    def __hash__(self):
        return hash(self.id)

    def view(self):
        return drink.template('main.html', obj=self,
            css=self.css, js=self.js, html=self.html,
            classes=self.classes, authenticated=request.identity)

    def struct(self, childs=True, full=None):
        return get_struct_from_obj(self, childs, full)

    @property
    def path(self):
        return self.rootpath + self.id + '/'

    def edit(self, resume=None):
        """ Edit form

        :arg resume: when given, won't call :meth:`_edit` but use this value instead
        :type resume: bool
        :returns: a form allowing to edit the object or http error

        call :meth:`_edit` method and return it's value.
        In case you return a tuple which first parameter is callable,
        then it calls the callable with the other tuple elements as parameters.
        This is used to handle redirects, from "inside" you should always use :meth:`_edit` !

        """
        r = resume or self._edit()
        transaction.commit() # commit before eventual redirect
        if isinstance(r, (list, tuple)) and callable(r[0]):
            return r[0](*r[1:])
        else:
            return r

    def _edit(self):
        if 'w' not in request.identity.access(self):
            return (drink.unauthorized, "Not authorized")

        items = self.editable_fields.items()
        if request.identity.id == self.owner.id or request.identity.admin:
            items += self.owner_fields.items()

        if request.identity.admin:
            items += self.admin_fields.items()

        forms = request.forms

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
                    caster.set(self, attr, forms.get(attr))

            database = drink.db.db
            if 'search' in database:
                database['search']._update_object(self)
            return (drink.rdr, self.path)
        else:
            if not items:
                form = ['<div class="error_message">Not editable, sorry...</div>']
            else:
                # sort by group+id
                items.sort(key=lambda o: o[1].group+o[0])
                current_group = None
                form_opts = []
                form = ['<input type="hidden" name="_dk_fields" value="%s">'%('/'.join(x[0] for x in items))]
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
                    form.append('<div class="input">%s</div>'%factory.html(field, val))
                form.append('''</div>
                <div class="buttons">
                <input class="submit" type="submit" value="Save changes please"/>
                </div></form>''')
                form.insert(0, '''<form
                 class="auto_edit_form" id="auto_edit_form" action="edit" %s method="post">'''%(' '.join(form_opts)))
            return drink.template('main.html', obj=self, html='\n'.join(form), css=self.css, js=self.js,
                 classes=self.classes, authenticated=request.identity)

    def _upload(self, obj):
        self.editable_fields['content'].set(self, 'content', obj)

    def upload(self):
        filename = request.GET.get('qqfile', None)
        if not filename:
            return {'error': True, 'message': 'Incorrect parameters. Action aborted.'}

        factory = self.upload_map.get(filename.rsplit('.')[-1], 'WebFile')

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
        name = request.GET.get('name')
        if not ('a' in request.identity.access(self) and 'w' in request.identity.access(self[name])):
            return drink.unauthorized("Not authorized")
        try:
            parent_path = self.path
        except AttributeError: # XXX: unclean
            parent_path = '.'
        old_obj = self[name]
        del self[name]
        transaction.commit()

        database = drink.db.db
        if 'search' in database:
            database['search']._del_object(old_obj)

        return drink.rdr(parent_path)

    def _add(self, name, cls, read_groups, write_groups):
        if isinstance(cls, basestring):
            klass = self.classes[cls] if self.classes else classes[cls]
        else:
            klass = cls
        new_obj = klass(name, self.path)
        if not new_obj.read_groups:
            new_obj.read_groups = set(read_groups)
        if not new_obj.write_groups:
            new_obj.write_groups = set(write_groups)

        self[new_obj.id] = new_obj
        database = drink.db.db
        if 'search' in database:
            database['search']._add_object(new_obj)

        transaction.commit()
        return new_obj

    def add(self, name=None, cls=None, read_groups=None, write_groups=None):
        auth = request.identity

        if 'a' not in auth.access(self):
            return drink.unauthorized("Not authorized")

        name = name or request.params.get('name')

        if name in self:
            drink.unauthorized("%r is already defined!"%name)

        if None == cls:
            cls = request.params.get('class')

        o = self._add(name, cls, auth.user.default_read_groups, auth.user.default_write_groups)
        if request.is_ajax:
            return o.struct()
        else:
            return drink.rdr(o.path+'edit')

    def list(self):
        return template('list.html', obj=self, css=self.css, js=self.js,
            classes=self.classes, authenticated=request.identity)

class ListPage(Page):
    description = "An ordered folder-like display"

    mime = "folder"

    forced_order = None

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
        self.forced_order = request.params.get('set').split('/')

    def itervalues(self):
        return (self[v] for v in self.keys())

    def values(self):
        return list(self.itervalues)

    def iteritems(self):
        for k in self.iterkeys():
            yield (k, self[k])

    def items(self):
        return list(self.iteritems)

    def reset_items(self):
        orig_order = []
        k = Page.keys(self)

        for item in self.forced_order:
            if item not in orig_order and item in k:
                orig_order.append(item)
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

    view = Page.list


class WebFile(Page):

    mime = "page"
    mimetype = "text/plain"
    description = "Some file"
    classes = {}

    owner_fields = {
        'read_groups':
            drink.types.GroupCheckBoxes("Read-enabled groups", group="x_permissions"),
        'write_groups':
            drink.types.GroupCheckBoxes("Write-enabled groups", group="x_permissions"),
        'mime': drink.types.Text(),
    }

    editable_fields = Page.editable_fields.copy()

    editable_fields.update( {
        'content':
            drink.types.File("File to upload"),
#        'content_name': drink.types.Text("File name"),
        'mimetype': drink.types.Text(),
    } )

    content = ''
    content_name = "unnamed"

    def raw(self):
        root, fname = os.path.split(self.content.filename)
        return drink.static_file(fname, root, mimetype=self.mimetype, download=self.content_name)
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

    def view(self):
        html = ['<div class="download"><a href="raw">Download file (original name: %r)</a></div>'%self.content_name]

        if self.content:
            mime = self.mimetype
            if mime.startswith('image/'):
                html.append('<img src="raw" />')
            elif mime in ('application/xml', ) or mime.startswith('text/'):
                f = self.content.open('r')
                html.append('<pre>')
                html.append(f.read())
                html.append('</pre>')

        return drink.template('main.html', obj=self, css=self.css, js=self.js, html='\n'.join(html),
             classes=self.classes, authenticated=request.identity)

exported = {'Folder index': ListPage, 'WebFile': WebFile}
