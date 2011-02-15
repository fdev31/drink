__all__ = ['_Editable',
    'Text', 'TextArea', 'GroupListArea', 'GroupCheckBoxes',
    'Id', 'Int', 'Password', 'File']

import os
from bottle import request, abort
from persistent.dict import PersistentDict
from ZODB.blob import Blob
import transaction
from drink import template
import drink
from . import classes

class _Editable(object):

    form_attr = None

    def __init__(self, caption=None, group=None):
        self.caption = caption
        self.id = str(id(self))
        self.group = group if group else self.__class__.__name__

    def html(self, name, value, _template=None):
        d = self.__dict__.copy()
        d.update({'id': self.id, 'name': name, 'caption': self.caption or name, 'value': value})
        return ('<div class="editable"><label class="autoform" for="%(id)s">%(caption)s:</label>'+(_template or self._template)+'</div>')%d

    set = setattr


class Text(_Editable):

    _template = r'''<input type="text" size="%(size)d" id="%(id)s" value="%(value)s" name="%(name)s" />'''

    def __init__(self, caption=None, group=None, size=40):
        _Editable.__init__(self, caption, group)
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
        if isinstance(value, basestring):
            length = value.count('\n')
        else:
            length = len(value)

        if c is None: # automatic mode
            self.cols = 50
        else:
            self.cols = c

        if r is None:
            self.rows = min(400, max(10, length))
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
        self._rows = len(value) + 2
        return TextArea.html(self, name, '\n'.join(group.id for group in value))

    def set(self, obj, name, val):
        groups = drink.db.db['groups']
        setattr(obj, name, set(groups[line.strip()] for line in val.split('\n') if line.strip() in groups))


class GroupCheckBoxes(_Editable):

    def html(self, name, value):
        groups = [g for g in drink.db.db['groups']]
        values = [v.id for v in value]

        opts = [r'<input type="checkbox" name=%(name)s value="'+o+'" '+\
            ('checked="checked" />' if o in values else '/><span class="label">')+o+'</span>' for o in groups]
        return _Editable.html(self, name, value, '\n'.join(opts))


    def set(self, obj, name, val):
        groups = request.forms.getall(name)
        dgroups = drink.db.db['groups']
        setattr(obj, name, set(dgroups[g] for g in groups))


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

class File(_Editable):
    _template = '<input name="%(name)s" id="%(id)s" type="file" />'

    form_attr = 'enctype="multipart/form-data"'

    def set(self, obj, name, val):
        if val == '':
            return
        setattr(obj, name+"_name", val.filename)
        new_o = Blob()
        setattr(obj, name, new_o)
        o_fd = new_o.open('w')
        chunk_sz = 2**20 # 1MB
        while True:
            dat = val.file.read(chunk_sz)
            if not dat:
                break
            o_fd.write(dat)
        o_fd.close()
