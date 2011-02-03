from UserDict import IterableUserDict
from ZODB.DB import DB
import transaction
import drink

class Database(IterableUserDict):

    def __init__(self, wsgi_app, storage):
        self.app = wsgi_app
        self._storage = storage
        self.app.add_hook('before_request', self.open_db)
        self.app.add_hook('after_request', self.close_db)
        self.connection = None

    def open_db(self):
        if not self.connection:
            self.connection = self.db.open()
            self.data = self.connection.root()
        transaction.begin()

    def close_db(self):
        transaction.commit()

    @property
    def db(self):
        storage = self._storage
        if isinstance(storage, basestring):
            from ZODB.FileStorage import FileStorage
            storage = FileStorage(storage)
        self.db = DB(storage)
        return self.db
