from __future__ import absolute_import
import os
from mimetypes import guess_type
from drink import request, abort
import transaction
import drink
from drink import template
from drink.zdb import Model
from . import classes

# TODO: make Model inherit Persistent + Page inherit PersistentDict
#  Model & Page will share most of the interface but Model can't have any children (it's an end-point property)
# ??? Models will be self-editable, wilth _Editable-like interface, they may have a link...

class _Mock(object): pass

def get_type(filename):
    return guess_type(filename)[0] or 'application/octet-stream'

class Page(Model):

    # Model properties

    editable_fields = {
        'title': drink.types.Text('Title'),
        'description': drink.types.Text('Description'),
    }

    owner_fields = {
        'easy_permissions':
            drink.types.EasyPermissions("EZ !", group="x_permissiona"),
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

    min_rights = ''

    mime = 'page'

    css = None

    js = None

    html = None

    description = 'An abstract page'

    classes = drink.classes

    # Model methods

    def __init__(self, name, rootpath=None):
        Model.__init__(self)
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
        return {
            # for upload function
            'success': True,
            # following describes the object:
            'path': o.rootpath, 'id': o.id, 'mime': 'page', 'title': o.title
        }

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
        database = drink.db.db
        if 'search' in database:
            database['search']._add_object(new_obj)

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


class ListPage(Page):
    description = "An ordered folder-like display"

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
