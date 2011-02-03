" Flaskbox "
from __future__ import absolute_import

import os

# bottle
import bottle
import transaction

from bottle import route, static_file, request, response, redirect, abort
from bottle import jinja2_view as view, jinja2_template as template
# set convenient alias (historical, compatibility with Flask)
rdr = redirect

from .config import BASE_DIR

bottle.TEMPLATE_PATH.append(os.path.join(BASE_DIR,'templates'))
STATIC_PATH = os.path.abspath(os.path.join(BASE_DIR, "static"))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, os.path.pardir, "database", "generic"))

class authenticated(object):

    __slots__ = ['user', 'success']

    def __init__(self):
        login = request.get_cookie('login', 'drink')
        try:
            self.user = db['users'][login]
        except KeyError:
            self.success = False
            self.user = None
        else:
            password = request.get_cookie('password', 'drink')
            self.success = self.user.password == password

    def access(self, obj):
        usr = self.user

        if usr == None:
            groups = [get_object(db, 'groups')['anonymous']]
        else:
            if usr.id == "admin":
                return 'rw'
            groups = usr.groups

        if usr == obj.owner:
            return 'rw'
        elif any(grp in groups for grp in obj.read_groups):
            return 'r'
        elif any(grp in groups for grp in obj.write_groups):
            return 'rw'
        return ''

    def __nonzero__(self):
        return self.success

# Finally load the objects


from .objects import classes, get_object, init as init_objects
from .objects.generic import Page, ListPage, Model, Text, TextArea
from .objects.generic import Id, Int, Password, GroupListArea
init_objects()

# ZODB3
from .zdb import Database
# init db
db = Database(bottle.app(), DB_PATH)

@route('/')
def main_index():
    request.identity = authenticated()
    return ListPage(db.data).view()

@route('/static/:filename#.*#')
def server_static(filename):
    return static_file(filename, root=os.path.join(BASE_DIR, 'static'))

@route("/login", method=['GET', 'POST'])
def log_in():
    response.set_cookie('password', request.forms.get('login_password', ''), 'drink')
    response.set_cookie('login', request.forms.get('login_name', ''), 'drink')
    rdr('/')

@route("/logout", method=['GET', 'POST'])
def log_out():
    response.set_cookie('password', '', 'drink')
    rdr('/')

@route("/:objpath#.+#")
def glob_index(objpath="/"):
    request.identity = authenticated()
    try:
        o = get_object(db.data, objpath)
    except AttributeError, e:
        abort(404, "%s not found"%e.args[0])

    if callable(o):
        return o()
    elif isinstance(o, basestring):
        return o
    else:
        return o.view()

def init():
    db.open_db()
    root = db.data
    from drink.config import config
    root.clear()

    from .objects import users

    class FakeId(object):
        user = None

        def access(self, obj):
            return 'rw'

    globals()['rdr'] = lambda *args: None

    request.identity = FakeId()
    root['groups'] = users.GroupList('groups', '/')
    transaction.commit()
    admin = users.User('admin', '/users/')
    request.identity.user = admin
    root['groups'].owner = admin
    root['users'] = users.UserList('users', '/')
    root['groups'].owner = admin
    root['users'].owner = admin

    root['users']['anonymous'] = users.User('anonymous', '/users/')

    admin.password = 'admin'
    admin.surname = "BOFH"
    admin.name = "Mr Admin"
    root['users']['admin'] = admin

    for pagename, name in config.items('layout'):
        elt = classes[ name ](pagename, '/')
        root[pagename] = elt
    transaction.commit()
