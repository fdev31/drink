from persistent.dict import PersistentDict

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

    def open_db(self):
        self.connection = self.db.open()
        self.data = self.connection.root()
        transaction.begin()

    def close_db(self):
        transaction.commit()
        del self.data
        self.connection.close()

    @property
    def db(self):
        storage = self._storage
        if isinstance(storage, basestring):
            from ZODB.FileStorage import FileStorage
            storage = FileStorage(storage)
        self.db = DB(storage)
        return self.db

class Model(PersistentDict):
    editable_fields = {}

    css = None

    js = None

    html = None

    def get(self):
        return dict(self)

    @property
    def path(self):
        return self.rootpath + self.id + '/'

    def edit(self):
        if drink.request.GET:
            get = drink.request.GET.get
        elif drink.request.POST:
            get = drink.request.POST.get
        else:
            get = None

        if get:
            for attr in self.editable_fields:
                v = get(attr)
                if v:
                    setattr(self, attr, v)
            transaction.commit()
            return drink.rdr(self.path)
        else:
            form = ['<form class="form" id="edit_form" action="edit" method="get">']
            for field, factory in self.editable_fields.iteritems():
                val = getattr(self, field)
                if isinstance(val, basestring):
                    form.append("<div>%s</div>"%factory.html(field, val))
            form.append('<div><input class="submit" type="submit" value="Ok"/></div></form>')
            return drink.template('main.html', obj=self, html='\n'.join(form), classes=drink.classes, authenticated=drink.authenticated())
