from __future__ import absolute_import
import drink
import fs
from fs.osfs import OSFS
from drink.objects.generic import get_struct_from_obj, get_type


class PyFile(object):
    description = u'File from disk'

    actions = []

    default_action = 'view'

    o = None

    _properties = ('edit', 'list', 'view', 'add', 'struct', 'actions')

    _v_mime = None

    _no_scan = True

    def __init__(self, parent_clone, parent_path, real_path, uuid, fd):
        self.o = parent_clone
        self.id = uuid
        self.title = uuid
        self.realpath = real_path
        self.rootpath = parent_path
        self.path = parent_path + uuid + '/'

    @property
    def mime(self):
        if not self._v_mime:
            self._v_mime = 'folder' if self.o.fd.isdir(self.realpath) else 'page'
        return self._v_mime

    @property
    def indexable(self):
        if isinstance(self.id, unicode):
            return self.id
        else:
            return self.id.decode('utf-8')

    def edit(self, *a):
        return self.view()

    def view(self, *a):
        if self.mime == 'folder':
            if 'index.html' in self.keys():
                return self['index.html'].view(*a)
            return drink.default_view(self, html='<div id="main_list" class="sortable" />')
        else:
            mime = get_type(self.id)

            if mime.startswith('text'):
                mime += ' ; charset=utf-8'
            else:
                drink.response.headers['Content-Disposition'] = 'attachment; filename="%s"'%self.id
            drink.response.headers['Content-Type'] = mime
            drink.response.headers['Content-Length'] = self.o.fd.getsize(self.realpath)
            if mime.split('/', 1)[0] == 'text':
                return self.o.fd.open(self.realpath, 'rb').read()
            else:
                root, fname = '/'.join((self.local_path, self.realpath)).rsplit('/', 1)
                return drink.static_file(fname, root, mimetype=mime, download=self.id)

    def struct(self, childs=True, full=None):
        return get_struct_from_obj(self, childs, full)

    def __getattr__(self, name):
        return getattr(self.o, name)

    def __getitem__(self, name):
        if name in self._properties:
            raise KeyError()
        return PyFile(self.o, self.path, self.realpath+'/'+name, name, self.o.fd)

    def __len__(self):
        try:
            return len(self.keys())
        except fs.errors.PermissionDeniedError:
            return 0

    def keys(self):
        if self.o.fd.isfile(self.realpath):
            return []
        else:
            return self.o.fd.listdir(self.realpath)

    iterkeys = keys

    def iteritems(self):
        return ( (k, self[k]) for k in self.keys() )

    def items(self):
        return list(self.iteritems())

    def itervalues(self):
        return (self[k] for k in self.keys())

    def values(self):
        return list(self.itervalues())


class Filesystem(drink.ListPage, PyFile):

    drink_name = 'Server folder'

    local_path = ''

    mime = 'folder'

    hidden_class = True

    path = ''

    editable_fields = drink.ListPage.editable_fields.copy()
    editable_fields.update({
        'local_path': drink.types.Text("Local folder path", group="a"),
    })

    def serialize(self):
        drink.ListPage.serialize(recurse=False)
        return d

    def __init__(self, name, rootpath):
        self.fd = None
        self.default_view = 'edit'
        drink.ListPage.__init__(self, name, rootpath)
        self._make_fd()
        PyFile.__init__(self, self, rootpath, self.id, self.id, None)

    def _edit(self):
        r = drink.ListPage._edit(self)
        self._make_fd()
        if self.fd:
            self.default_view = 'list'
        return r

    def _make_fd(self):
        if self.local_path and not self.fd:
            try:
                self.fd = OSFS(self.local_path, thread_synchronize=True)
            except fs.errors.ResourceNotFoundError:
                self.fd = None

    def keys(self):
        if self.fd:
            return self.fd.listdir()
        else:
            return []

    iterkeys = keys

    def __getattr__(self, name):
        return drink.Model.__getattribute__(self, name)

    def __getitem__(self, name):
        if name in self._properties:
            raise KeyError()
        return PyFile(self, self.path, name, name, self.fd)
