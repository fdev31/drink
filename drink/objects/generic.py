from __future__ import absolute_import
import os
from mimetypes import guess_type
from bottle import request, abort
from persistent.dict import PersistentDict
from ZODB.blob import Blob
import transaction
from drink import template
import drink
from . import classes

# TODO: make Model inherit Persistent + Page inherit PersistentDict
#  Model & Page will share most of the interface but Model can't have any children (it's an end-point property)
# ??? Models will be self-editable, wilth _Editable-like interface, they may have a link...

class Model(PersistentDict):

    editable_fields = {
        'title': drink.types.Text('Title')
    }


    owner_fields = {
        'read_groups':
            drink.types.GroupCheckBoxes("Read-enabled groups", group="x_permissions"),
        'write_groups':
            drink.types.GroupCheckBoxes("Write-enabled groups", group="x_permissions")
    }

    admin_fields = {
        'id': drink.types.Id(),
    }

    css = None

    js = None

    html = None

    mime = 'model'

    data = {}

    classes = drink.classes

    def __init__(self, name, rootpath=None):
        self.read_groups = set()
        self.write_groups = set()

        if not name:
            drink.abort(401, 'Wrong identifier: %r'%name)

        if not isinstance(name, basestring):
            # Root object special case
            PersistentDict.__init__(self, name)
            name = '/'
            rootpath = '/'
        else:
            PersistentDict.__init__(self)

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

    def __setitem__(self, name, val):
        if name in self:
            abort(401, "%r is already defined!"%name)
        PersistentDict.__setitem__(self, name, val)

    def view(self):
        return "Not viewable"

    def struct(self, childs=True):

        d = dict()
        for k in self.editable_fields.keys():
            v = getattr(self, k, None)
            if isinstance(v, Model):
                v = v.struct(False)
                v['id'] = k
            elif isinstance(v, (basestring, int, float)):
                pass # serializes well in json
            else:
                v = "N/A"
            d[k] = v


        if childs:
            it = [v.struct() for v in self.itervalues()]
            if it:
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
                current_group = items[0][1].group
                form_opts = []
                form = []
                for field, factory in items:
                    if factory.form_attr:
                        form_opts.append(factory.form_attr)
                    if factory.group != current_group:
                        current_group = factory.group
                        form.append('</div><div class="%s_grp">'%current_group)
                    val = getattr(self, field, '')
                    form.append('<div class="input">%s</div>'%factory.html(field, val))
                form.append('</div><div class="buttons"><input class="submit" type="submit" value="Save changes please"/></div></form>')
                form.insert(0, '<form class="auto_edit_form" id="auto_edit_form" action="edit" %s method="post"><div class="%s_grp">'%(' '.join(form_opts), current_group))
            return drink.template('main.html', obj=self, html='\n'.join(form), css=self.css, js=self.js, classes=self.classes, authenticated=request.identity)


class Page(Model):

    mime = 'page'

    doc = 'An abstract page'

    def rm(self):
        name = request.GET.get('name')
        if 'w' not in request.identity.access(self[name]):
            return abort(401, "Not authorized")
        try:
            parent_path = self.path
        except AttributeError:
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

        if 'w' not in auth.access(self):
            return abort(401, "Not authorized")
        name = name or request.GET.get('name')
        if None == cls:
            cls = request.GET.get('class')

        return drink.rdr(self._add(name, cls, auth.user.read_groups, auth.user.write_groups).rootpath)

    def view(self):
        return 'Not viewable...'


class ListPage(Page):
    doc = "An ordered folder-like display"

    mime = "folder"

    forced_order = None

    js = ['/static/listing.js']

    def __init__(self, name, rootpath=None):
        Page.__init__(self, name, rootpath)
        self.forced_order = list(Page.keys(self))

    def iterkeys(self):
        return iter(self.forced_order or Page.keys(self))

    keys = iterkeys

    def move(self):
        self.forced_order = request.forms.get('set').split('/')

    def itervalues(self):
        return (self[v] for v in self.keys())

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
        'content_name': drink.types.Text("File name"),
        'mimetype': drink.types.Text(),
    } )

    content = ''
    content_name = "unnamed"

    def raw(self):
        root, fname = os.path.split(self.content.committed())
        return drink.static_file(fname, root, mimetype=self.mimetype, download=self.content_name)
        #Alternatively: drink.response.headers['Content-Type'] = '...'
        # + read

    def edit(self):
        r = Page._edit(self)
        if request.files:
            self.mimetype = guess_type(request.files.get('content').filename)[0] or 'application/octet-stream'
        transaction.commit()
        return Page.edit(self, r)

    def view(self):
        html = ['<div class="download"><a href="raw">Download file (original name: %r)</a></div>'%self.content_name]

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
