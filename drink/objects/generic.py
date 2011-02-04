from __future__ import absolute_import
__all__ = ['Page', 'ListPage', 'Model',
    'Text', 'TextArea', 'Id' ]

from bottle import request, abort
from persistent.dict import PersistentDict
import transaction
from drink import template
import drink
from . import classes

class _Editable(object):

    def __init__(self, caption=None, group=None):
        self.caption = caption
        self.id = str(id(self))
        self.group = group if group else self.__class__.__name__

    def html(self, name, value):
        d = self.__dict__.copy()
        d.update({'id': self.id, 'name': name, 'caption': self.caption or name, 'value': value})
        return ('<label class="autoform" for="%(id)s">%(caption)s</label>'+self._template)%d

    set = setattr


class Text(_Editable):

    _template = r'''<input type="text" size="%(size)d" id="%(name)s" value="%(value)s" name="%(name)s" />'''

    def __init__(self, caption=None, group=None, size=40):
        _Editable.__init__(self, caption)
        self.size = 40


class TextArea(_Editable):
    _template = '''<textarea rows="%(rows)s" cols="%(cols)s" id="%(id)s" name="%(name)s">%(value)s</textarea>'''

    def __init__(self, caption=None, group=None, rows=None, cols=None):
        _Editable.__init__(self, caption, group)
        self._rows = rows
        self._cols = cols

    def html(self, name, value):
        r = self._rows
        c = self._cols
        if c is None: # automatic mode
            self.cols = 100
        else:
            self.cols = c

        if r is None:
            self.rows = min(400, max(10, len(value.split('\n'))))
        else:
            self.rows = r

        return _Editable.html(self, name, value)

#class MultilineList(TextArea):
#    def html(self, name, value):
#        return TextArea.html(self, name, '\n'.join(value))
#
#    def set(self, obj, name, val):
#        setattr(obj, name, [line.strip() for line in val.split('\n') if line.strip()])

class GroupListArea(TextArea):
    def html(self, name, value):
        self._cols = 30
        return TextArea.html(self, name, '\n'.join(group.id for group in value))

    def set(self, obj, name, val):
        groups = drink.db['groups']
        setattr(obj, name, set(groups[line.strip()] for line in val.split('\n') if line.strip() in groups))


class Id(Text):
    def set(self, obj, name, val):
        parent = drink.get_object(drink.db, obj.rootpath)
        del parent[getattr(obj, name)]
        setattr(obj, name, val)
        parent[val] = obj

class Int(Text):
    def set(self, obj, name, val):
        setattr(obj, name, int(val))

class Password(Text):
    _template = r'''<input type="password" size="%(size)d" id="%(id)s" name="%(name)s" value="%(value)s" />'''


class Model(PersistentDict):

    editable_fields = {
        'read_groups': GroupListArea("Read-enabled groups", group="x_permissions"),
        'write_groups': GroupListArea("Write-enabled groups", group="x_permissions")
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

        if request.GET:
            get = request.GET.get
        elif request.POST:
            get = request.POST.get
        else:
            get = None

        if get:
            for attr, caster in self.editable_fields.iteritems():
                v = get(attr)
                if v:
                    caster.set(self, attr, v)
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

                form = ['<form class="edit_form" id="edit_form" action="edit" method="get"><div class="%s_grp">'%current_group]
                for field, factory in items:
                    if factory.group != current_group:
                        current_group = factory.group
                        form.append('</div><div class="%s_grp">'%current_group)
                    val = getattr(self, field)
                    form.append('<div class="input">%s</div>'%factory.html(field, val))
                form.append('</div><div class="buttons"><input class="submit" type="submit" value="Ok"/></div></form>')
            return drink.template('main.html', obj=self, html='\n'.join(form), classes=self.classes, authenticated=request.identity)


class Page(Model):

    mime = 'page'

    doc = 'An abstract page'

    @property
    def title(self):
        return self.id.replace('_', ' ').replace('-', ' ')

    def rm(self):
        if 'w' not in request.identity.access(self):
            return abort(401, "Not authorized")
        name = request.GET.get('name')
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


exported = {'Folder index': ListPage}
