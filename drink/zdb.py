from UserDict import IterableUserDict
import ZODB.config
import transaction
import drink

class Database(IterableUserDict):

    def __init__(self, wsgi_app, conf_file):
        self.app = wsgi_app
        self._config = conf_file
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
        self.db = ZODB.config.databaseFromURL(self._config)
        return self.db
