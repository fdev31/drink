from __future__ import absolute_import
import drink
import fs
from fs.osfs import OSFS
from drink.objects.generic import get_struct_from_obj, Model, guess_type

class PyFile(object):
    description = 'File from disk'
    min_rights = ''

    def __init__(self, parent_clone, parent_path, real_path, uuid, fd):
        self.o = parent_clone
        self.id = uuid
        self.title = uuid
        self.realpath = real_path
        self.rootpath = parent_path
        self.path = parent_path + uuid + '/'
        if self.o.fd.isdir(self.realpath):
            self.mime = 'folder'
        else:
            self.mime = 'page'

    def view(self):
        if self.mime == 'folder':
            return drink.template('list.html', obj=self, css=[], js=[],
                classes={}, authenticated=drink.request.identity)
        else:
            drink.response.headers['Content-Type'] = guess_type(self.id)
            drink.response.headers['Content-Length'] = self.o.fd.getsize(self.realpath)

            CZ = 2**20
            fd = self.o.fd.open(self.realpath)
            while True:
                data = fd.read(CZ)
                if not data:
                    break
                return data

    def struct(self, childs=True, full=None):
        return get_struct_from_obj(self, childs, full)

    def __getattr__(self, name):
        return getattr(self.o, name)

    def __getitem__(self, name):
        if name in ('edit', 'list', 'view', 'struct'):
            raise KeyError()
        return PyFile(self.o, self.path, self.realpath+'/'+name, name, self.o.fd)

    def __len__(self):
        try:
            return len(self.keys())
        except fs.PermissionDeniedError:
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

class Filesystem(PyFile, drink.ListPage):

    local_path = ''
    default_view = 'list'
    mime = 'folder'
    hidden_class = True

    editable_fields = drink.ListPage.editable_fields.copy()
    editable_fields.update({
        'local_path': drink.types.Text("Local folder path", group="a"),
    })

    def __init__(self, name, rootpath):
        drink.ListPage.__init__(self, name, rootpath)
        PyFile.__init__(self, self, rootpath, self.id, self.id, None)

    def _edit(self):
        r = drink.ListPage._edit(self)
        self.fd = OSFS(self.local_path, thread_synchronize=True)
        return r

    def keys(self):
        if self.local_path:
            return self.fd.listdir()
        else:
            return []

    iterkeys = keys

    def __getattr__(self, name):
        return Model.__getattribute__(self, name)

    def __getitem__(self, name):
        if name in ('edit', 'list', 'view', 'struct'):
            raise KeyError()
        return PyFile(self, self.path, name, name, self.fd)

exported = {'Server folder': Filesystem}
