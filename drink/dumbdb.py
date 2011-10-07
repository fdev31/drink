__all__ = ['transaction', 'Model', 'Database', 'DataBlob', 'BTree', 'PersistentList']

import logging
import tempfile
import os
import atexit
import pickle

log = logging.getLogger('dumbdb')

PersistentList = list
class Model(dict): pass
BTree = Model

class DataBlob(object):
    def __init__(self, orig_blob=None):
        fd, self.filename = tempfile.mkstemp(prefix="dk_blob_")

    def open(self, mode='r'):
        return open(self.filename, mode)


class Database(object):

    db = None

    def __init__(self, wsgi_app, config_file):
        pass

    def pack(self):
        _save_db()

    def start_request(self, *a):
        if Database.db is None:
            Database.db = Model()
            try:
                d = pickle.load(open('_db.p'))
            except:
                pass
            else:
                if d:
                    Database.db.update(d)
                    log.info("Loaded %r", Database.db)
        return Database.db
    close_request = __exit__ = __enter__ = start_request


class Transaction(object):
    # TODO: implement transactions
    def commit(self):
        pass
    def rollback(self):
        pass

transaction = Transaction()

def _save_db():
    f = open('_db.p', 'w')
    log.info("Saving %r", Database.db)
    pickle.dump(Database.db, f)
    f.close()

atexit.register(_save_db)
