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
        self.locals.__dict__.setdefault('c', None)
        self.locals.__dict__.setdefault('root', None)
        self._db = None
        self.connection = None
        wsgi_app.add_hook('before_request', self.start_request)
        wsgi_app.add_hook('after_request', self.close_request)
        atexit.register(self._cleanup)

    def _cleanup(self):
        if self._db:
            self._db.close()
        if self.locals.c:
            self.locals.c.close()
        self.app.hooks.clear()

    def __del__(self):
        self._cleanup()

    @property
    def db(self):
        if self._db is None:
            self._db = ZODB.config.databaseFromURL(self._config)

        r = self.locals.root

        if not self.locals.c:
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
        self.locals.c.close()
        self.locals.c = None

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            transaction.abort()
        else:
            transaction.commit()
        self.close_request()
