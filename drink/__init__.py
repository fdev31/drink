" Drink "
from __future__ import absolute_import, with_statement

# configuration time
from drink.config import config, BASE_DIR

# bottle & db setup

import bottle
import os

bottle.TEMPLATE_PATH.append(os.path.join(BASE_DIR,'templates'))
STATIC_PATH = os.path.abspath(os.path.join(BASE_DIR, "static"))
DB_PATH = config.get('server', 'database') or os.path.abspath(os.path.join(BASE_DIR, os.path.pardir, "database"))
DB_CONFIG = os.path.join(DB_PATH, "zodb.conf")

# auto-guess & set datadir in case of inchanged default
lines = open(DB_CONFIG).readlines()
pattern = '%define DATADIR database\n'

try:
    i = lines.index(pattern)
except ValueError:
    i = -1
if i >= 0:
    lines[i] = '%%define DATADIR %s\n'%DB_PATH
    open(DB_CONFIG, 'w').writelines(lines)

# Import main modules used + namespace setup

# http
from bottle import route, static_file, request, response, redirect as rdr, abort
# templating
import functools
template = functools.partial(bottle.template, req=request, template_adapter=bottle.Jinja2Template)

# Load Basic objects
from .objects import classes, get_object, init as init_objects
from . import types
from .objects.generic import Page, ListPage, Model

# Finally load all the objects

init_objects()
del init_objects

# Setup db

from .zdb import Database
db = Database(bottle.app(), DB_CONFIG)
import transaction

def unauthorized(message='Action NOT allowed'):
    if request.identity:
        raise abort(401, message)
    else:
        rdr('/')

# Declare "drink" wsgi loader
class DrinkServer(bottle.ServerAdapter):
    """ Drink-flavored bottle runner.
    Will try gevent, paste, bjoern >=1.1, rocket, fapws3 or wsgiref (in this order)
    """
    adapters = [bottle.GeventServer, bottle.PasteServer,
        bottle.RocketServer, bottle.FapwsServer, bottle.WSGIRefServer]

    def run(self, handler):
        adapters = list(self.adapters)

#        try:
#            import bjoern
#        except ImportError:
#            pass
#        else:
#            if bjoern.version >= (1, 1, 0):
#                adapters.insert(1, bottle.BjoernServer)


        for sa in adapters:
            try:
                print "* Trying %s"%sa.__name__
                return sa(self.host, self.port, **self.options).run(handler)
            except ImportError:
                pass

bottle.server_names['drink'] = DrinkServer

# Real code starts here

class Authenticator(object):

    __slots__ = ['user', 'success', 'groups', 'admin', 'id']

    def __init__(self):
        login = request.get_cookie('login', 'drink')
        # TODO: handle basic http auth digest
        try:
            self.user = db.db['users'][login]
        except KeyError:
            self.success = False
        else:
            password = request.get_cookie('password', 'drink')
            self.success = self.user.password == password

        if self.success:
            self.groups = self.user.groups.copy()
            self.groups.add('users')
            self.admin = 'admin' in self.groups or self.user.id == 'admin'
        else:
            self.user = db.db['users']['anonymous']
            self.admin = False
            self.groups = set()

        self.groups.add('anonymous')

        self.id = self.user.id

    def access(self, obj):
        """
        owner
        write
        add(& delete if owner)
        read
        traversal
        """

        groups = self.groups
        rights = ''

        if self.admin or self.id == obj.owner.id:
            rights = 'owart'
        elif groups.intersection(obj.write_groups):
            rights = 'wart'
        elif self.success and 'users' in obj.write_groups:
            rights = 'wrt'
        elif groups.intersection(obj.read_groups):
            rights = 'rt'

        return rights+obj.min_rights

    def __nonzero__(self):
        return self.success


# Root routing functions

@route('/')
def main_index():
    request.identity = Authenticator()
    o = classes[config.get('server', 'index')](db.db, rootpath='/')
    o.disable_ajax = True
    return o.view()

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

# generic dispatcher method
@route("/:objpath#.+#", method=['GET', 'POST'])
def glob_index(objpath="/"):
    request.identity = Authenticator()
    try:
        o = get_object(db.db, objpath)
    except AttributeError, e:
        abort(404, "%s not found"%objpath)

    if callable(o):
        return o()
    elif isinstance(o, basestring):
        response.content_type = "text/plain"
        return o
    else:
        return getattr(o, o.default_action)()

def init():
    from drink.objects.finder import reset
    reset()
    with db as root:
        root.clear()

        from .objects import users as obj

        class FakeId(object):
            user = None

            def access(self, obj):
                return 'rowat'

        request.identity = FakeId()
        groups = root['groups'] = obj.GroupList('groups', '/')
        users = root['users'] = obj.UserList('users', '/')
        root['groups']['users'] = obj.Group('users', '/groups/')

        admin = obj.User('admin', '/users/')
        request.identity.user = admin

        anon = obj.User('anonymous', '/users/')

        groups.owner = admin
        groups.read_groups = set()
        groups.write_groups = set()

        users.owner = admin
        users.read_groups = set()
        users.write_groups = set()
        users.min_rights = 't'

        root['users']['anonymous'] = anon
        root['users']['admin'] = admin

        admin.password = 'admin'
        admin.surname = "BOFH"
        admin.name = "Mr Admin"
        admin.owner = admin

        anon.groups = set()
        anon.owner = admin

        users = root['groups']['users']
        users.owner = admin
        users.read_groups = set()
        users.write_groups = set()
        users.min_rights = 't'

        for pagename, name in config.items('layout'):
            elt = classes[ name ](pagename, '/')
            root[pagename] = elt

        if 'pages' in root:
            mdown = classes['Web page (markdown)']('help', '/pages/')
            help = os.path.abspath(os.path.join(BASE_DIR, os.path.pardir, "HELP.md"))
            mdown.content = open(help).read()
            mdown.owner = admin
            mdown.min_rights = 'r'
            root['pages']['help'] = mdown


def startup():
    import sys

    try:
        import setproctitle
    except ImportError:
        print "Unable to set process' name, easy_install setproctitle, if you want it."
    else:
        setproctitle.setproctitle('drink')

    # handle commands
    # TODO: create "update" command
    if len(sys.argv) == 2 and sys.argv[1] == "help":
        print """
Drink help

commands:
    init: reset database
    pack: pack database (more compact/faster)
    debug: run a debugger after loading
    help: this help :)

Without any argument, it will just run the server.
if DEBUG environment variable is set, it will start in debug mode.
        """
    elif len(sys.argv) == 2 and sys.argv[1] == "init":
        init()
        db.pack()
    elif len(sys.argv) == 2 and sys.argv[1] == "pack":
        db.pack()
    elif len(sys.argv) == 2 and sys.argv[1] == "debug":
        from pdb import set_trace
        with db as root:
            set_trace()
    else:
        dbg_in_env = 'DEBUG' in os.environ

        if not dbg_in_env and 'BOTTLE_CHILD' not in os.environ:

            reset_required = False

            with db as c:
                if len(c) < 3:
                    reset_required = True

            if reset_required:
                init()

        for name, klass in classes.items():
            if getattr(klass, 'hidden_class', False):
                del classes[name]

        # And now, http/wsgi part

        host = config.get('server', 'host')
        port = int(config.get('server', 'port'))
        mode = config.get('server', 'backend')

        # try some (optional) asynchronous optimization

        async = False

        if dbg_in_env:
            mode = 'debug'

        if mode not in ('debug', 'paste', 'rocket'):
            try:
                import gevent.monkey
                gevent.monkey.patch_all()
            except ImportError:
                async = False
            else:
                async = True

        config.async = async

        app = bottle.app()

        # handle debug mode
        debug = False
        if dbg_in_env:
            debug = True
            # trick to allow debug-wrapping
            app.catchall = False

            def dbg_repoze(app):
                from repoze.debug.pdbpm import PostMortemDebug
                app = PostMortemDebug(app)
                print "Installed repoze.debug's debugging middleware"
                return app

            def dbg_werkzeug(app):
                from werkzeug.debug import DebuggedApplication
                app = DebuggedApplication(app, evalex=True)
                print "Installed werkzeug debugging middleware"
                return app

            def dbg_weberror(app):
                from weberror.evalexception import EvalException
                app = EvalException(app)
                print "Installed weberror debugging middleware"
                return app

            dbg_backend = config.get('server', 'debug')

            if dbg_backend == 'auto':
                backends = [dbg_werkzeug, dbg_repoze, dbg_weberror]
            else:
                backends = [locals()['dbg_%s'%dbg_backend]]

            # debug middleware loading
            for loader in backends:
                try:
                    app = loader(app)
                    break
                except ImportError:
                    continue
            else:
                print "Unable to install the debugging middleware, current setting: %s"%dbg_backend
        # /end dbg_in_env

        #from wsgiauth.ip import ip
        #@ip
        #def authenticate(env, ip_addr):
        #    return ip_addr == '127.0.0.1'
        #
        #app = authenticate(app)

        # Let's run !
        bottle.debug(debug)
        bottle.run(app=app, host=host, port=port, reloader=debug, server='wsgiref' if mode == 'debug' else mode)
