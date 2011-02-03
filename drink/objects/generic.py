from __future__ import absolute_import
__all__ = ['Page', 'ListPage', 'Model',
    'Text', 'TextArea', 'Id' ]

from bottle import request, abort
from persistent.dict import PersistentDict
import transaction
from drink import template, authenticated
import drink
from . import classes

class _Editable(object):

    def html(self, name, value):
        d = self.__dict__.copy()
        d.update({'name': name, 'value': value})
        return self._template%d

    set = setattr
    #def set(self, obj, name, val):
        #setattr(obj, name, val)


class Text(_Editable):

    _template = r'''<label for="%(name)s_class">%(name)s</label>
    <input type="text" size="%(size)d" id="%(name)s_class" value="%(value)s" name="%(name)s" />'''

    def __init__(self, size=40):
        self.size = 40


class TextArea(_Editable):
    _template = '''<label for="%(name)s_class">%(name)s</label>
    <textarea rows="%(rows)s" cols="%(cols)s" id="%(name)s_class" name="%(name)s">%(value)s</textarea>'''

    def __init__(self, rows=None, cols=None):
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
        groups = drink.get_object(drink.db, 'groups')
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
    _template = r'''<label for="passwd%(name)s">%(name)s:</label>
        <input type="password" size="%(size)d" id="%(name)s_class" name="%(name)s" value="%(value)s" />'''


class Model(PersistentDict):
    editable_fields = {'read_groups': GroupListArea(), 'write_groups': GroupListArea()}

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
                form = ['<form class="edit_form" id="edit_form" action="edit" method="get">']
                for field, factory in self.editable_fields.iteritems():
                    val = getattr(self, field)
                    form.append("<div>%s</div>"%factory.html(field, val))
                form.append('<div><input class="submit" type="submit" value="Ok"/></div></form>')
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

    def add(self, name=None, cls=None):
        if 'w' not in request.identity.access(self):
            return abort(401, "Not authorized")
        name = name or request.GET.get('name')
        if None == cls:
            cls = request.GET.get('class')

        if isinstance(cls, basestring):
            klass = classes[cls]
        else:
            klass = cls
        new_obj = klass(name, self.path)
        self[name] = new_obj
        transaction.commit()
        return drink.rdr(new_obj.rootpath)

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
        return template('list.html', obj=self, classes=classes, authenticated=request.identity)


exported = {'Folder index': ListPage}
