from __future__ import absolute_import
import os
from bottle import request, abort
from persistent.dict import PersistentDict
from ZODB.blob import Blob
import transaction
from drink import template
import drink
from . import classes


class Model(PersistentDict):

    editable_fields = {
        'read_groups':
            drink.types.GroupCheckBoxes("Read-enabled groups", group="x_permissions"),
        'write_groups':
            drink.types.GroupCheckBoxes("Write-enabled groups", group="x_permissions")
    }

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
        return dict(self)

    @property
    def path(self):
        return self.rootpath + self.id + '/'

    def edit(self):
        if 'w' not in request.identity.access(self):
            return abort(401, "Not authorized")

        if request.POST:
            get = request.POST.get
        elif request.GET:
            get = request.GET.get
        else:
            get = None

        if get:
            for attr, caster in self.editable_fields.iteritems():
                caster.set(self, attr, get(attr))
            transaction.commit()
            return drink.rdr(self.path)
        else:
            if not self.editable_fields:
                form = ['<div>Not editable, sorry...</div>']
            else:
                items = self.editable_fields.items()
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
                form.append('</div><div class="buttons"><input class="submit" type="submit" value="Ok"/></div></form>')
                form.insert(0, '<form class="edit_form" id="edit_form" action="edit" %s method="post"><div class="%s_grp">'%(' '.join(form_opts), current_group))
            return drink.template('main.html', obj=self, html='\n'.join(form), classes=self.classes, authenticated=request.identity)


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

    def _add(self, name, cls):
        if isinstance(cls, basestring):
            klass = self.classes[cls] if self.classes else classes[cls]
        else:
            klass = cls
        new_obj = klass(name, self.path)
        self[name] = new_obj
        transaction.commit()
        return new_obj

    def add(self, name=None, cls=None):
        if 'w' not in request.identity.access(self):
            return abort(401, "Not authorized")
        name = name or request.GET.get('name')
        if None == cls:
            cls = request.GET.get('class')

        return drink.rdr(self._add(name, cls).rootpath)

    def view(self):
        return 'Please, inherit...'


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
        return template('list.html', obj=self, classes=self.classes, authenticated=request.identity)


class StaticFile(Page):

    mime = "page"
    mimetype = "text/plain"
    doc = "A generic file"
    classes = {}

    editable_fields = {
        'read_groups':
            drink.types.GroupListArea("Read-enabled groups", group="x_permissions"),
        'write_groups':
            drink.types.GroupListArea("Write-enabled groups", group="x_permissions"),
        'content':
            drink.types.File("File to upload"),
        'mimetype': drink.types.Text(),
        'mime': drink.types.Text(),
    }

    content = ''
    content_name = "unnamed"

    def raw(self):
        root, fname = os.path.split(self.content.committed())
        return drink.static_file(fname, root, mimetype=self.mimetype)
        #Alternatively: drink.response.headers['Content-Type'] = '...'
        # + read

    def view(self):
        if self.mimetype.startswith('image/'):
            html = '<img src="raw" />'
        else:
            html = '<a href="raw">Download file %r!</a>'%self.content_name

        return drink.template('main.html', obj=self, html=html, classes=self.classes, authenticated=request.identity)

    def struct(self):
        return dict((k, getattr(self, k+"_name", 'N/A')) for k, v in self.editable_fields.iteritems() if isinstance(v, File))


exported = {'Folder index': ListPage, 'File': StaticFile}
