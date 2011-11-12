__all__ = ['transaction', 'Model', 'Database', 'DataBlob', 'BTree', 'PersistentList']

from UserDict import IterableUserDict
import ZODB.config
import logging
import transaction
import persistent
import drink
import atexit
import threading
from ZODB.blob import Blob
# Not used, but exported
from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList

log = logging.getLogger('Database')

class Database(object):
    def __init__(self, wsgi_app, config_data):
        log.info('New database instance')
        self.app = wsgi_app
        self._config = config_data
        self.locals = threading.local()
        self._db = None
        self.connection = None
        wsgi_app.hooks.add('before_request', self.start_request)
        wsgi_app.hooks.add('after_request', self.close_request)
        atexit.register(self._cleanup)

    def _cleanup(self):
        log.info('CLEAN')
        if self._db:
            self._db.close()
        if getattr(self.locals, 'c', None):
            self.locals.c.close()
        self.app.hooks.remove('before_request', self.start_request)
        self.app.hooks.remove('after_request', self.close_request)
        self._cleanup = lambda: 1

    def __del__(self):
        self._cleanup()

    def pack(self):
        self.db # KEEPME: loads the database
        return self._db.pack()

    @property
    def db(self):
        if self._db is None:
            self._db = ZODB.config.databaseFromString(self._config)

        r = getattr(self.locals, 'root', None)

        if None == r:
            c = self.locals.c = self._db.open()
            r = self.locals.root = c.root()

        return r

    def start_request(self):
        log.info('ENTER')
        d = self.db
        transaction.begin()
        return d

    __enter__ = start_request

    def close_request(self):
        log.info('CLOSE')
        transaction.commit()

    def __exit__(self, exc_type, exc_value, traceback):
        log.info('EXIT')
        if exc_value:
            transaction.abort()
        else:
            transaction.commit()

class DataBlob(persistent.Persistent):
    def __init__(self, orig_blob=None):
        self._o = orig_blob if orig_blob != None else Blob()

    def open(self, mode='r'):
        """ Opens the blob, returns a file descriptor """
        return self._o.open(mode)

    @property
    def filename(self):
        return self._o.committed()

BTree = OOBTree

class Model(persistent.Persistent):

    # Dict-like methods

    def __repr__(self):
        return repr(self.data)

    def __cmp__(self, dict):
        if isinstance(dict, Model):
            return cmp(self.data, dict.data)
        else:
            return cmp(self.data, dict)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.data[key] = item
        self._p_changed = 1

    def __delitem__(self, key):
        del self.data[key]
        self._p_changed = 1

    def clear(self):
        self.data.clear()
        self._p_changed = 1

    def copy(self):
        if self.__class__ is Model:
            return Model(self.data.copy())
        import copy
        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data
        c.update(self)
        return c

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def iteritems(self):
        return self.data.iteritems()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def values(self):
        return self.data.values()

    def has_key(self, key):
        return key in self.data

    def update(self, other=None, **kwargs):

        if other != None:
            if isinstance(other, Model):
                self.data.update(other.data)
            else:
                self.data.update(other)

        if len(kwargs):
            self.data.update(kwargs)

        self._p_changed = 1

    def get(self, key, failobj=None):
        if key not in self:
            return failobj
        return self[key]

    def setdefault(self, key, failobj=None):
        if key not in self:
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        r = self.data.pop(key, *args)
        self._p_changed = 1
        return r

    def popitem(self):
        r = self.data.popitem()
        self._p_changed = 1
        return r

    def __contains__(self, key):
        return key in self.data

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __iter__(self):
        return iter(self.data)
