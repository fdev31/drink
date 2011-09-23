__all__ = ['_Editable',
    'Text', 'TextArea', 'GroupListArea', 'GroupCheckBoxes',
    'Mime', 'Choice',
    'Date',
    'Id', 'Int', 'Password', 'File']

import os
import drink
import datetime
import transaction
from . import classes
from drink import omni
from drink.zdb import DataBlob
from time import mktime, strptime
from persistent.dict import PersistentDict

class _Editable(object):

    form_attr = None

    def __init__(self, caption=None, group=None):
        self.caption = caption
        self.id = str(id(self))
        self.group = group if group else self.__class__.__name__

    def html(self, name, value, _template=None, no_label=False):
        d = self.__dict__.copy()
        d.update({'id': self.id, 'name': name, 'caption': self.caption or name, 'value': value})
        if no_label:
            pfx = '<div id="edit_%(name)s" class="editable">'
        else:
            pfx = '<div id="edit_%(name)s" class="editable">\
                <label class="autoform" for="%(id)s">%(caption)s:</label>'

        return (pfx+(_template or self._template)+'</div>')%d

    def get(self, obj, name):
        return getattr(obj, name)

    def set(self, obj, name, val):
        setattr(obj, name, drink.omni(val))


class Choice(_Editable):

    _template = None

    def __init__(self, caption=None, options=None, group=None):
        if options is None:
            raise ValueError('Choice must get an options parameter which is either a dict or a list of tuples ((label, value),(label2, value2),...)! (you can also use a callable returning the attribute)')
        if isinstance(options, dict): # unordered dict
            self._options = options.items()
        else: # ordered list of tuples
            self._options = options
        _Editable.__init__(self, caption, group)

    def html(self, name, value, _template=None, no_label=False):
        if callable(self._options):
            o = self._options()
        else:
            o = self._options

        options = '\n'.join('<option value="%s" %s>%s</option>'%(
                v[1],
                ' selected="selected" ' if v[1] == value else '',
                v[0])
            for v in o)

        return _Editable.html(self, name, value,
            _template=r'<select class="select" id="%(id)s" name="%(name)s">'+options+r'</select>',
            no_label=no_label)

class Mime(Choice):
    _options = dict((k.capitalize(), k) for k in '''executable
            folder
            group
            groups
            markdown
            note
            page
            search
            tasks
            user'''.split())

    def __init__(self, caption="Icon", options=None, group=None):
        if options is None:
            options = self._options
        Choice.__init__(self, caption, options, group)

class Text(_Editable):

    _template = r'''<input type="%(_type)s" size="%(size)d" id="%(id)s" value="%(value)s" name="%(name)s" />'''

    _type = None

    def __init__(self, caption=None, group=None, size=40, type="text"):
        _Editable.__init__(self, caption, group)
        self.size = size
        self._type = type

DATE_FMT = r'%d/%m/%Y'

#DATETIME_FMT = r'%d/%m/%Y %H:%M'


def dt2str(dt):
    try:
        return dt.strftime(DATE_FMT)
    except AttributeError: # str
        return dt


def dt2ts(dt):
    try:
        return int(mktime(dt.timetuple()))
    except AttributeError: # str
        return 0


def str2dt(text):
     #TODO: use DATETIME_FMT
    try:
        return datetime.datetime(*strptime(text, DATE_FMT)[:6])
    except AttributeError:
        return text

def str2d(text):
    try:
        return datetime.date(*strptime(text, DATE_FMT)[:3])
    except AttributeError:
        return text

class Date(Text):

    _template = r'''<input class="auto_date" type="text" size="%(size)d" id="%(id)s" value="%(value)s" name="%(name)s" />'''

    def __init__(self, caption=None, group=None):
        Text.__init__(self, caption, group)

    def set(self, obj, name, val):
        setattr(obj, name, str2d(val))

    def get(self, obj, name):
        return dt2str(getattr(obj, name))

    def html(self, name, value, _template=None, no_label=False):
        return Text.html(self, name, dt2str(value), _template, no_label)


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


class BoolOption(_Editable):
    def html(self, name, value):
        html = r'<input type="checkbox" name=%(name)s value="%(name)s"'+\
            ('checked="checked" />' if value else '/>')+r'<span class="bool'+\
            (' selected' if value else '')+r'">%(caption)s</span>'
        return _Editable.html(self, name, None, _template=html, no_label=True)

    def set(self, obj, name, val):
        setattr(obj, name, bool(val))


class CheckboxSet(_Editable):

    def __init__(self, caption=None, group=None, options=None):
        """ values: set of valid Ids (or tuple (caption,value) or a dict of {caption: value}
                OR a callable returning this object """
        _Editable.__init__(self, caption, group)
        self.options = options

    @property
    def v(self):
        if callable(self.options):
            o = self.options()
        else:
            o = self.options

        if isinstance(o, dict):
            return o.items()
        else:
            return [(v,v) for v in o]

    def html(self, name, values):

        opts = [r'<input type="checkbox" name=%(name)s value="'+o[1]+'" '+\
            ('checked="checked" />' if o[1] in values else '/>')+'<span class="label'+\
            (' '+'selected' if o[1] in values else '')+r'">'+o[0]+'</span>'
            for o in self.v]
        return _Editable.html(self, name, None, '\n'.join(opts))

    def set(self, obj, name, val):
        values = drink.request.forms.getall(name)
        all_values = set(o[1] for o in self.v)
        all_values.intersection_update(values)
        setattr(obj, name, all_values)


class GroupCheckBoxes(CheckboxSet):

    def __init__(self, caption=None, group=None):
        CheckboxSet.__init__(self, caption, group, self._group_list)

    def _group_list(self):
        return drink.db.db['groups'].keys()


class Id(Text):
    def set(self, obj, name, val):
        parent = drink.get_object(drink.db, obj.rootpath)
        del parent[getattr(obj, name)]
        setattr(obj, name, val)
        parent[val] = obj


class Int(Text):
    def set(self, obj, name, val):
        setattr(obj, name, int(val))


class Float(Text):
    def set(self, obj, name, val):
        float(val) # validates float
        setattr(obj, name, val)

class Duration(Text):
    def set(self, obj, name, val):
        if val.endswith('d'):
            val = float(val[:-1])*24
        elif val.endswith('w'):
            val = float(val[:-1])*24*7
        float(val) # validates float
        setattr(obj, name, val)


class Password(Text):
    _template = r'''<input type="password" size="%(size)d" id="%(id)s" name="%(name)s" value="%(value)s" />'''


class File(_Editable):
    _template = '<input name="%(name)s" id="%(id)s" type="file" />'

    form_attr = 'enctype="multipart/form-data"'

    def set(self, obj, name, val):
        if val == '':
            return
        elif isinstance(val, DataBlob):
            new_o = val
        else:
            fname = omni(val.filename)
            setattr(obj, name+"_name", fname)
            new_o = DataBlob()
            o_fd = new_o.open('w')
            chunk_sz = 2**20 # 1MB
            while True:
                dat = val.file.read(chunk_sz)
                if not dat:
                    break
                o_fd.write(dat)
            o_fd.close()

        setattr(obj, name, new_o)

class EasyPermissions(_Editable):
    def html(self, name, value, _template=None):
        return """<ul>
        <li class="option" onclick="$('#edit_read_groups input').each( function() { $(this).attr('checked', false ) } ) ; $('#edit_write_groups input').each( function() { $(this).attr('checked', false ) } )">
        Reset (this document will only be accessible from your account)</li>
        <li class="option" onclick="$('#edit_read_groups input').each( function() { $(this).attr('checked', !! $(this).attr('value').match(/^users|admin$/) ) } ) ; $('#edit_write_groups input').each( function() { $(this).attr('checked', false ) } ) ">
        Viewable by registered users</li>
        <li class="option" onclick="$('#edit_read_groups input').each( function() { $(this).attr('checked', !! $(this).attr('value').match(/^users|admin$/) ) } ) ; $('#edit_write_groups input').each( function() { $(this).attr('checked', !! $(this).attr('value').match(/^users|admin$/) ) } ) ">
        Viewable and Editable by registered users</li>
        <li class="option" onclick="$('#edit_read_groups input').each( function() { $(this).attr('checked', !! $(this).attr('value').match(/^users|anonymous|admin$/) ) } ) ">
        Everybody can view the document</li>
        </ul>
        <div class="option" id="show_hide_permissions" onclick="var o=$('#show_hide_permissions'); var g=$('.x_permissions_grp'); if(g.css('display') == 'none') {o.html('Hide detailed permissions')} else {o.html('Show detailed permissions')}; g.slideToggle('slow');">
        Show detailed permissions</div>
        """

    def set(self, obj, name, val):
        return
