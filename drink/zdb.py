from UserDict import IterableUserDict
import ZODB.config
import transaction
import drink
import atexit
import threading

class Database(object):
    def __init__(self, wsgi_app, config_file):
        self.app = wsgi_app
        self._config = config_file
        self.locals = threading.local()
        self._db = None
        self.connection = None
        wsgi_app.add_hook('before_request', self.start_request)
        wsgi_app.add_hook('after_request', self.close_request)
        atexit.register(self._cleanup)


    def _cleanup(self):
        if self._db:
            self._db.close()
        if getattr(self.locals, 'c', None):
            self.locals.c.close()
        self.app.hooks.clear()

    def __del__(self):
        self._cleanup()

    def pack(self):
        return self._db.pack()

    @property
    def db(self):
        if self._db is None:
            self._db = ZODB.config.databaseFromURL(self._config)

        r = getattr(self.locals, 'root', None)

        if None == r:
            c = self.locals.c = self._db.open()
            r = self.locals.root = c.root()

        return r

    def start_request(self):
        d = self.db
        transaction.begin()
        return d

    __enter__ = start_request

    def close_request(self):
        transaction.commit()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            transaction.abort()
        else:
            transaction.commit()
