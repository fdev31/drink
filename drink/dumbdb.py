__all__ = ['transaction', 'Model', 'Database', 'DataBlob', 'BTree', 'PersistentList']

import tempfile

PersistentList = list
class Model(dict): pass
BTree = Model

class DataBlob(object):
    def __init__(self, orig_blob=None):
        fd, self.filename = tempfile.mkstemp()

    def open(self, mode='r'):
        return open(self.filename, mode)


class Database(object):
    def __init__(self, wsgi_app, config_file):
        self.db = Model()

    def pack(self):
        pass

    def start_request(self, *a): return self.db
    close_request = __exit__ = __enter__ = start_request


class Transaction(object):
    # TODO: implement transactions
    def commit(self):
        pass
    def rollback(self):
        pass

transaction = Transaction()
