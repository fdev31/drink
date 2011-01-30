" Flaskbox "
from __future__ import absolute_import

import os

# bottle
import bottle
import transaction

from bottle import route, static_file, request, response, redirect, abort
from bottle import jinja2_view as view, jinja2_template as template

# ZODB3
from .zdb import Database
from .config import BASE_DIR

bottle.TEMPLATE_PATH.append(os.path.join(BASE_DIR,'templates'))
STATIC_PATH = os.path.abspath(os.path.join(BASE_DIR, "static"))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, os.path.pardir, "database", "generic"))

# set convenient alias (historical, compatibility with Flask)
rdr = redirect

# init db
db = Database(bottle.app(), DB_PATH)

def authenticated():
    login = request.get_cookie('login', 'drink')
    passwd = request.get_cookie('password', 'drink')

    return  login == passwd == 'admin'

# Finally load the objects


from .objects import classes, get_object
from .objects.generic import ListPage

@route('/')
def main_index():
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
    response.set_cookie('password', '')
    rdr('/')

@route("/:objpath#.+#")
def glob_index(objpath="/"):
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

def __init_():
    from flaskbox.config import config

    db.open_db()
    root = db.data

    root.clear()

    for pagename, name in config.items('layout'):
        elt = classes[ name ]()
        elt.id = pagename
        elt.rootpath = '/'
        root[pagename] = elt
    transaction.commit()
