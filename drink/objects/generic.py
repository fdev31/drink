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


class Model(PersistentDict):

    owner_fields = {
        'read_groups':
            drink.types.GroupCheckBoxes("Read-enabled groups", group="x_permissions"),
        'write_groups':
            drink.types.GroupCheckBoxes("Write-enabled groups", group="x_permissions")
    }

    editable_fields = {}

    css = None

    js = None

    html = None

    data = {}

    classes = drink.classes

    def __init__(self, name, rootpath=None):
        self.read_groups = set()
        self.write_groups = set()

        if rootpath is None:
            PersistentDict.__init__(self, name)
            self.id = getattr(name, 'id', '')
            self.rootpath = getattr(name, 'rootpath', '')
        else:
            PersistentDict.__init__(self)
            self.id = name
            self.rootpath = rootpath

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

    def struct(self):
        return 'Not defined'

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

        if request.POST:
            get = request.POST.get
        elif request.GET:
            get = request.GET.get
        else:
            get = None

        items = self.editable_fields.items()
        if request.identity.user.id == self.owner.id \
            or request.identity.user.id == "admin":
            items += self.owner_fields.items()

        if get:
            for attr, caster in items:
                caster.set(self, attr, get(attr))
            transaction.commit()
            return (drink.rdr, self.path)
        else:
            if not self.editable_fields:
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
                    val = getattr(self, field)
                    form.append('<div class="input">%s</div>'%factory.html(field, val))
                form.append('</div><div class="buttons"><input class="submit" type="submit" value="Save changes please"/></div></form>')
                form.insert(0, '<form class="auto_edit_form" id="auto_edit_form" action="edit" %s method="post"><div class="%s_grp">'%(' '.join(form_opts), current_group))
            return drink.template('main.html', obj=self, html='\n'.join(form), css=self.css, js=self.js, classes=self.classes, authenticated=request.identity)


class Page(Model):

    mime = 'page'

    doc = 'An abstract page'

    @property
    def title(self):
        return self.id.replace('_', ' ').replace('-', ' ')

    def rm(self):
        name = request.GET.get('name')
        if 'w' not in request.identity.access(self[name]):
            return abort(401, "Not authorized")
        parent_path = self[name].path+".."
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
        self[name] = new_obj

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
    doc = "An ordered folder display"

    mime = "folder"

    forced_order = None

    def iterkeys(self):
        if not self.forced_order:
            self.forced_order = list(self.keys())
        return self.forced_order

    def __setitem__(self, name, val):
        if name in self.forced_order:
            self.forced_order.remove(name)
        self.forced_order.append(name)
        return Page.__setitem__(self, name, val)

    def __delitem__(self, name):
        self.forced_order.remove(name)
        return Page.__delitem__(self, name)

    def view(self):
        return template('list.html', obj=self, css=self.css, js=self.js, classes=self.classes, authenticated=request.identity)

    def struct(self):
        return {'items': self.forced_order, 'mime': self.mime}

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

    editable_fields = {
        'content':
            drink.types.File("File to upload"),
        'mimetype': drink.types.Text(),
    }

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

    def struct(self):
        return dict((k, getattr(self, k+"_name", 'N/A')) for k, v in self.editable_fields.iteritems() if isinstance(v, File))


exported = {'Folder index': ListPage, 'File': StaticFile}
