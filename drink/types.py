__all__ = ['_Editable',
    'Text', 'TextArea', 'GroupListArea', 'GroupCheckBoxes',
    'CheckboxSet', 'BoolOption',
    'Mime', 'Choice', 'Link',
    'Date',
    'Id', 'Int', 'Password', 'File']

import os
import drink
import datetime
from drink import omni
from time import mktime, strptime

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

    def __repr__(self):
        return "drink.types.%s(%r, group=%r)"%(self.__class__.__name__, self.caption, self.group)

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

    _template = r'''<input type="%(_type)s" size="%(size)d" style="width:%(size)dex" id="%(id)s" value="%(value)s" name="%(name)s" />'''

    _type = None

    def __init__(self, caption=None, group=None, size=40, type="text"):
        _Editable.__init__(self, caption, group)
        self.size = size
        self._type = type


class Link(Text):

    _template = '''<input type="%(_type)s" size="%(size)d" style="width:%(size)dex" id="%(id)s" value="%(value)s" name="%(name)s" class="completable" complete_type="objpath" />'''

    def __init__(self, caption=None, group=None, size=60, type="text"):
        Text.__init__(self, caption, group, size, type)


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
    except ValueError:
        return datetime.datetime.now()

def str2d(text):
    try:
        return datetime.date(*strptime(text, DATE_FMT)[:3])
    except AttributeError:
        return text
    except ValueError:
        return datetime.date.today()

class Date(Text):

    _template = r'''<input class="auto_date" type="text" size="%(size)d" style="width:%(size)dex" id="%(id)s" value="%(value)s" name="%(name)s" />'''

    def __init__(self, caption=None, group=None):
        Text.__init__(self, caption, group, size=12)

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
        Text.set(self, obj, name, val)

from hashlib import sha1
import re
hex_re = re.compile('[0-9a-f]{40}')

class Password(Text):
    _template = r'''<input type="password" size="%(size)d" id="%(id)s" name="%(name)s" value="%(value)s" />'''

    def set(self, obj, name, val):
        if not hex_re.match(val):
            val = sha1(val).hexdigest()
        setattr(obj, name, val)

class File(_Editable):
    _template = '<input name="%(name)s" id="%(id)s" type="file" />'

    form_attr = 'enctype="multipart/form-data"'

    def set(self, obj, name, val):
        if val == '':
            return
        elif isinstance(val, drink.DataBlob):
            new_o = val
        else:
            fname = omni(val.filename)
            setattr(obj, name+"_name", fname)
            new_o = drink.DataBlob()
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
        return """
        <script type="text/javascript">
        $(document).ready (function() {
        $(function() {
            $.toggle_perm( $('#perm_fr_r'), '%(id)s', 'r', true);
            $.toggle_perm( $('#perm_fr_w'), '%(id)s', 'w', true);
            $.toggle_perm( $('#perm_any_r'), 'users', 'r', true);
            $.toggle_perm( $('#perm_any_w'), 'users', 'w', true);
            $.toggle_perm( $('#perm_ano_r'), 'anonymous', 'r', true);
            $.toggle_perm( $('#perm_ano_w'), 'anonymous', 'w', true);
        });

        $.extend({
            'toggle_perm': function(me, who, mode, simulate) {
                var a = [];
                var g = {'matches': 0}
                if (mode.match(/r/)) {
                    a.push('read');
                };
                if (mode.match(/w/)) {
                    a.push('write');
                };
                console.log(who);
                console.log(mode);
                var r = RegExp('^'+who+'$');
                for (i=0;i<a.length;i++) {
                    $('#edit_'+a[i]+'_groups input').each(function() {
                        if ( $(this).attr('value').match(r) ) {
                            if($(this).is(':checked'))
                                g['matches'] += 1;
                        }
                })};
                var cur_val = g['matches'] != 0;
                console.log('val '+cur_val);
                if (!simulate) {
                    for (i=0;i<a.length;i++) {
                        $('#edit_'+a[i]+'_groups input').each(function() {
                            console.log(this);
                             if ( $(this).attr('value').match(r) ) {
                                $(this).attr('checked', !cur_val);
                             }
                        });
                    };
                   $(me).toggleClass('selected', !cur_val);
                } else {
                   $(me).toggleClass('selected', cur_val);
                }

        }});
        });
        </script>
        <ul id="ez_perm_list">
        <strong>Friends can:</strong>
        <li id="perm_fr_r" onclick="$.toggle_perm(this, '%(id)s', 'r')" class="option">View this document</li>
        <li id="perm_fr_w" class="option" onclick="$.toggle_perm(this, '%(id)s', 'w')">Edit this document</li>

        <strong>Any registered user can:</strong>
        <li id="perm_any_r" onclick="$.toggle_perm(this, 'users', 'r')"class="option">View this document</li>
        <li id="perm_any_w" onclick="$.toggle_perm(this, 'users', 'w')"class="option">Edit this document</li>

        <strong>Everybody can:</strong>
        <li id="perm_ano_r" onclick="$.toggle_perm(this, 'anonymous', 'r')" class="option">View this document</li>
        <li id="perm_ano_w" onclick="$.toggle_perm(this, 'anonymous', 'w')" class="option">Edit this document</li>

        <div>
        <script type="text/javascript">
        function apply_perms(from) {
            var fo=$('#auto_edit_form');
            var o=$('<input type="hidden" name="_recurse" value="1"></input>');
            fo.append(o);
            fo.submit();
        }
        </script>
        <span class="button" id="apply_permissions_recursively" onclick="apply_perms(this)">Save and Apply permissions on children</span>
        </div>

        <span class="button" id="show_hide_permissions" onclick="var o=$('#show_hide_permissions'); var g=$('.x_permissions_grp'); if(g.css('display') === 'none') {o.html('Hide detailed permissions');  g.fadeIn('slow');} else { g.hide(); o.html('Show detailed permissions')};">
        Show detailed permissions</span>

        """%dict(id=drink.request.identity.id)

    def set(self, obj, name, val):
        return
