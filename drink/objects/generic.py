from __future__ import absolute_import
import os
from mimetypes import guess_type
from bottle import request, abort
from ZODB.blob import Blob
#from persistent.dict import PersistentDict
import persistent
from persistent.mapping import default
import transaction
from drink import template
import drink
from . import classes

# TODO: make Model inherit Persistent + Page inherit PersistentDict
#  Model & Page will share most of the interface but Model can't have any children (it's an end-point property)
# ??? Models will be self-editable, wilth _Editable-like interface, they may have a link...

class _Mock(object): pass

def get_type(filename):
    return guess_type(filename)[0] or 'application/octet-stream'

class Model(persistent.Persistent):

    # Dict-like methods

    def __init__(self, name, rootpath=None):
        persistent.Persistent.__init__(self)
        self.data = {}
        self.read_groups = set()
        self.write_groups = set()

        if not isinstance(name, basestring):
            # Root object special case, will pass the dict or None...
            if name is not None:
                self.update(name)
            name = '/'
            rootpath = '/'
            self.id = '.'
        else:
            if not name or name[0] in r'/.$%_':
                drink.abort(401, 'Wrong identifier: %r'%name)
            # minor sanity check
            self.id = name.replace(' ', '-').replace('\t','_').replace('/','.').replace('?', '')

        self.rootpath = rootpath

        if not hasattr(self, 'title'):
            self.title = name.replace('_', ' ').replace('-', ' ').capitalize()

        try:
            self.owner
        except AttributeError:
            self.owner = request.identity.user

    def __repr__(self):
        return repr(self.data)

    def __cmp__(self, dict):
        if isinstance(dict, Model):
            return cmp(self.data, dict.data)
        else:
            return cmp(self.data, dict)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        if key in self:
            abort(401, "%r is already defined!"%key)
        self.data[key] = item
        self._p_changed = 1

    def __delitem__(self, key):
        del self.data[key]
        self._p_changed = 1

    def clear(self):
        self.data.clear()
        self._p_changed = 1

    def copy(self):
        if self.__class__ is Model:
            return Model(self.data.copy())
        import copy
        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data
        c.update(self)
        return c

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def iteritems(self):
        return self.data.iteritems()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def values(self):
        return self.data.values()

    def has_key(self, key):
        return key in self.data

    def update(self, dict=None, **kwargs):
        if dict is None:
            pass
        elif isinstance(dict, Model):
            self.data.update(dict.data)
        elif isinstance(dict, type({})) or not hasattr(dict, 'items'):
            self.data.update(dict)
        else:
            for k, v in dict.items():
                self[k] = v
        if len(kwargs):
            self.data.update(kwargs)
        self._p_changed = 1

    def get(self, key, failobj=None):
        if key not in self:
            return failobj
        return self[key]

    def setdefault(self, key, failobj=None):
        if key not in self:
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        r = self.data.pop(key, *args)
        self._p_changed = 1
        return r

    def popitem(self):
        r = self.data.popitem()
        self._p_changed = 1
        return r

    def __contains__(self, key):
        return key in self.data

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __iter__(self):
        return iter(self.data)

    # Model properties

    editable_fields = {
        'title': drink.types.Text('Title')
    }

    owner_fields = {
        'read_groups':
            drink.types.GroupCheckBoxes("Read-enabled groups", group="x_permissions"),
        'min_rights':
            drink.types.Text("Every user's permissions (wrta)", group="x_permissions"),
        'write_groups':
            drink.types.GroupCheckBoxes("Write-enabled groups", group="x_permissions")
    }

    admin_fields = {
        #'id': drink.types.Id(),
    }

    css = None

    js = None

    html = None

    mime = 'model'

    classes = drink.classes

    min_rights = ''

    # Model methods

    def __hash__(self):
        return hash(self.id)

    def view(self):
        return "Not viewable"

    def struct(self, childs=True):

        a = request.identity.access

        d = dict()

        if 'r' in a(self):
            for k in self.editable_fields.keys():
                v = getattr(self, k, None)
                if isinstance(v, Model):
                    if not 'r' in a(v):
                        continue
                    v = v.struct(False)
                    v['id'] = k
                elif isinstance(v, (basestring, int, float)):
                    pass # serializes well in json
                else:
                    v = "N/A"
                d[k] = v


            if childs:
                it = [v.struct() for v in self.itervalues() if 'r' in a(v)]
                d['items'] = it

        d['id'] = self.id
        d['title'] = self.title
        d['path'] = self.rootpath
        d['mime'] = self.mime

        return d

    @property
    def path(self):
        return self.rootpath + self.id + '/'

    def edit(self, resume=None):
        r = resume or self._edit()
        transaction.commit() # commit before eventual redirect
        if callable(r[0]):
            return r[0](*r[1:])
        else:
            return r

    def _edit(self):
        if 'w' not in request.identity.access(self):
            return abort(401, "Not authorized")

        items = self.editable_fields.items()
        if request.identity.id == self.owner.id or request.identity.admin:
            items += self.owner_fields.items()

        if request.identity.admin:
            items += self.admin_fields.items()

        forms = request.forms

        if forms:
            editable = forms.keys()
            files = request.files.keys()

            for attr, caster in items:
                if attr in files:
                    caster.set(self, attr, request.files.get(attr))
                elif attr in editable:
                    caster.set(self, attr, forms.get(attr))

            transaction.commit()
            return (drink.rdr, self.path)
        else:
            if not items:
                form = ['<div class="error_message">Not editable, sorry...</div>']
            else:
                # sort by group+id
                items.sort(key=lambda o: o[1].group+o[0])
                current_group = None
                form_opts = []
                form = []
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
                form.append('</div><div class="buttons"><input class="submit" type="submit" value="Save changes please"/></div></form>')
                form.insert(0, '<form class="auto_edit_form" id="auto_edit_form" action="edit" %s method="post">'%(' '.join(form_opts)))
            return drink.template('main.html', obj=self, html='\n'.join(form), css=self.css, js=self.js, classes=self.classes, authenticated=request.identity)

class Page(Model):

    mime = 'page'

    doc = 'An abstract page'

    def upload(self):
        filename = request.GET.get('qqfile', 'uploaded')
        o = self._add(filename, 'File',
            request.identity.user.default_read_groups,
            request.identity.user.default_write_groups)
        fake_post_obj = _Mock()
        fake_post_obj.file = request.body
        fake_post_obj.filename = filename
        o.editable_fields['content'].set(o, 'content', fake_post_obj)
        o.mimetype = get_type(fake_post_obj.filename)
        return {'success': True, # for upload function
        # following describes the object:
        'path': o.rootpath, 'id': o.id, 'mime': 'page', 'title': o.title}

    def rm(self):
        name = request.GET.get('name')
        if not ('a' in request.identity.access(self) and 'w' in request.identity.access(self[name])):
            return abort(401, "Not authorized")
        try:
            parent_path = self.path
        except AttributeError: # XXX: unclean
            parent_path = '.'
        del self[name]
        transaction.commit()
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

        transaction.commit()
        return new_obj

    def add(self, name=None, cls=None, read_groups=None, write_groups=None):
        auth = request.identity

        if 'a' not in auth.access(self):
            return abort(401, "Not authorized")
        name = name or request.GET.get('name')
        if None == cls:
            cls = request.GET.get('class')

        return drink.rdr(self._add(name, cls, auth.user.default_read_groups, auth.user.default_write_groups).rootpath)

    def view(self):
        return 'Not viewable...'


class ListPage(Page):
    doc = "An ordered folder-like display"

    mime = "folder"

    forced_order = None

    js = ['/static/listing.js']

    def __init__(self, name, rootpath=None):
        self.forced_order = []
        Page.__init__(self, name, rootpath)

    def iterkeys(self):
        k = Page.keys(self)
        return (x for x in self.forced_order if x in k) or k

    keys = iterkeys

    def move(self):
        self.forced_order = request.params.get('set').split('/')

    def itervalues(self):
        return (self[v] for v in self.keys())

    def reset_items(self):
        orig_order = []
        k = Page.keys(self)

        for item in self.forced_order:
            if item not in orig_order and item in k:
                orig_order.append(item)
        self.forced_order = orig_order
        return 'ok'

    def values(self):
        return list(self.itervalues)

    def __setitem__(self, name, val):
        if name is None:
            import pdb; pdb.set_trace()
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

    def view(self):
        return template('list.html', obj=self, css=self.css, js=self.js, classes=self.classes, authenticated=request.identity)

class StaticFile(Page):

    mime = "page"
    mimetype = "text/plain"
    doc = "A generic file"
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
        root, fname = os.path.split(self.content.committed())
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
                f = self.content.open()
                html.append('<pre>')
                html.append(f.read())
                html.append('</pre>')

        return drink.template('main.html', obj=self, css=self.css, js=self.js, html='\n'.join(html), classes=self.classes, authenticated=request.identity)

exported = {'Folder index': ListPage, 'File': StaticFile}
