" Drink "
from __future__ import absolute_import, with_statement

# imports + basic configuration

import os
import logging
logging.basicConfig()

import signal
signal.signal(signal.SIGPIPE, signal.SIG_IGN)

dbg_in_env = 'DEBUG' in os.environ
if dbg_in_env:
    logging.getLogger().setLevel(logging.NOTSET)
else:
    logging.getLogger().setLevel(logging.WARNING)

log = logging.getLogger('core')

from drink.config import config, BASE_DIR
import tempfile
import bottle

# some globals
classes = {}
bottle.TEMPLATE_PATH.append(os.path.join(BASE_DIR,'templates'))
STATIC_PATH = os.path.abspath(os.path.join(BASE_DIR, "static"))
DB_PATH = config.get('server', 'database') or os.path.abspath(os.path.join(BASE_DIR, os.path.pardir, "database"))


# auto-guess & set datadir in case of inchanged default
log.debug("Using DB informations from %s", DB_PATH)
def _fix_datadir(txt):
    try:
        i = txt.index('%define DATADIR database\n')
    except ValueError:
        i = -1
    if i >= 0:
        txt[i] = '%%define DATADIR %s\n'%DB_PATH
    return ''.join(txt)

DB_CONFIG = _fix_datadir(open(os.path.join(DB_PATH, "zodb.conf")).readlines())

# Import main modules used + namespace setup

# http
from bottle import route, static_file, request, response, redirect as rdr, abort
# templating
from urllib import unquote
# json
dumps = bottle.JSONPlugin().json_dumps

def bytes2human(num):
    for u in ('k', 'M', 'G'):
        num /= 1000.0
        if num < 951:
            break
    return u'%.1f %s'%(num, u)

def omni(txt):
    if isinstance(txt, unicode):
        return txt
    else:
        txt = unquote(txt)
        try:
            return txt.decode('utf-8')
        except UnicodeError:
            return txt.decode('latin1')

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

        settings = Settings('settings', '/')
        settings.server_backend = config.get('server', 'backend')
        settings.server_port = int(config.get('server', 'port'))
        settings.server_address = config.get('server', 'host')
        settings.debug_framework = config.get('server', 'debug')
        settings.active_objects = set(config.items('objects'))

        root['settings'] = settings

        root['pages'] = Page('pages', '/')

        # deploy layout
        for pagename, name in config.items('layout'):
            root[pagename] = classes[ name ](pagename, '/')

        mdown = classes['Web page (markdown)']('help', '/pages/')
        help = os.path.abspath(os.path.join(BASE_DIR, os.path.pardir, "HELP.md"))
        mdown.content = open(help).read()
        mdown.owner = admin
        mdown.min_rights = 'r'
        root['pages']['help'] = mdown

# Setup db
reset_required = False
try:
    from . import zdb
    del zdb
    PERSISTENT_STORAGE = True
except ImportError:
    PERSISTENT_STORAGE = False
    from .dumbdb import Database, DataBlob, Model, transaction
else:
    from .zdb import Database, DataBlob, Model, transaction
db = Database(bottle.app(), DB_CONFIG)

# Load Basic objects
from .objects.generic import Page, ListPage, Settings
from .objects import classes as obj_classes, get_object, init as init_objects
from . import types
def add_upload_handler(ext, obj_name):
    if isinstance(ext, basestring):
        ext = [ext]
    for e in ext:
        Page.upload_map[e] = obj_name

# Finally load all the objects
init_objects()
classes.update(obj_classes)
del init_objects, obj_classes

def unauthorized(message='Action NOT allowed', code=401):
    # TODO: handler srcuri + redirect
    if request.identity:
        return {'error': True, 'message': message, 'code': code}
    else:
        return rdr('/login?from='+request.path)

#import cgi
#def escape(text):
#    """ Escapes the given string """
#    # TODO: in python3, use html.escape
#    assert isinstance(text, unicode)
#    return cgi.escape(text).encode('ascii', 'xmlcharrefreplace')

# Declare "drink" wsgi loader
class DrinkServer(bottle.ServerAdapter):
    """ Drink-flavored bottle runner.
    Will try gevent, paste, bjoern >=1.2, rocket, fapws3 or wsgiref (in this order)
    """
    adapters = [bottle.GeventServer, bottle.PasteServer,
        bottle.RocketServer, bottle.FapwsServer, bottle.WSGIRefServer]

    def run(self, handler):
        adapters = list(self.adapters)

        try:
            bjoern_req_version = (1, 2, 0)
            import bjoern
        except ImportError:
            log.info("You can try installing bjoern >= %s", '.'.join(str(x) for x in bjoern_req_version))
        else:
            if bjoern.version >= bjoern_req_version:
                adapters.insert(1, bottle.BjoernServer)


        for sa in adapters:
            try:
                log.debug("* Trying %s"%sa.__name__)
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
    rdr('/pages/')

@route('/static/:filename#.*#')
def server_static(filename):
    # TODO: add authentication filter here ?
    return static_file(filename, root=os.path.join(BASE_DIR, 'static'))

@route("/struct", method=['GET', 'POST'])
def login_struct():
    return {}

@route("/actions", method=['GET', 'POST'])
def login_actions():
    return []

@route("/login", method=['GET', 'POST'])
def log_in():
    request.identity = Authenticator()

    if request.forms.get('login_name', ''):
        response.set_cookie('password', request.forms.get('login_password', ''), 'drink')
        response.set_cookie('login', request.forms.get('login_name', ''), 'drink')
        url = request.params.get('from', '/')
        rdr(url)
    else:
        html='''
        <h1>Connect to drink</h1>
        <form name="login_form" id="login_form" class="autovalidate" action="/login" method="post">
            <div class="label"><label for="ilogin">Authenticate as:</label></div>
            <div><input type="text" class="required" name="login_name" id="ilogin" /></div>
            <div class="label"><label for="ipasswd">Password:</label></div>
            <div><input type="password" class="required" name="login_password" id="ipassword" /></div>
            <div><input type="hidden" name="from" value="%s" /></div>
            <div><input class="submit" type="submit" value="Log in!"/></div>
        </form>

        '''%request.params.get('from', '/')
        return bottle.jinja2_template('main.html', html=html, obj=db.db, css=[], js=[],
            isstring=lambda x: isinstance(x, basestring),
            embed='', classes={}, req=request, authenticated=request.identity)


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
        return abort(404, "%s not found"%objpath)

    if callable(o):
        o = o()

    t = type(o)

    if t == dict:
        if not request.is_ajax:
            if 'redirect' in o:
                return rdr(o['redirect'])
            if 'error' in o:
                return abort(o['code'], o['message'])
        response.content_type = "application/json"
        return dumps(o)
    elif isinstance(o, Model):
        try:
            return getattr(o, o.default_action)()
        except AttributeError:
            o = o[o.default_action]
            return getattr(o, o.default_action)()
    elif t in (list, tuple):
        response.content_type = "application/json"
        return dumps(o)
    return o


def startup():
    import sys

    try:
        import setproctitle
    except ImportError:
        log.warning("Unable to set process' name, easy_install setproctitle, if you want it.")
    else:
        setproctitle.setproctitle('drink')

    # handle commands
    # TODO: create "update" command
    if len(sys.argv) == 2 and sys.argv[1] == "help":
        print """
Drink help

commands:
    run: starts the server
    init: reset database
    pack: pack database (more compact/faster)
    rebuild: EXPERIMENTAL, will try to convert & clean an old database to newer format
    export: EXPERIMENTAL, will try to dump all the data into the given folder
    debug: run a debugger after loading
    help: this help :)

Without any argument, it will just run the server.
if DEBUG environment variable is set, it will start in debug mode.
        """
    elif len(sys.argv) == 2 and sys.argv[1] == "init":
        init()
        db.pack()
    elif len(sys.argv) == 2 and sys.argv[1] == "db":
        fd, fname = tempfile.mkstemp(suffix=".conf")
        os.write(fd, _fix_datadir(open(os.path.join(DB_PATH, 'zeo.conf')).readlines()))
        os.close(fd)
        os.system('zeoctl -C %s start'%fname)
        os.unlink(fname)
    elif len(sys.argv) == 2 and sys.argv[1] == "pack":
        from drink.objects import finder
        finder.init()
        finder.indexer.optimize()
        db.pack()
    elif len(sys.argv) == 2 and sys.argv[1] == "rebuild":

        from .zdb import Blob

        if not 'settings' in db.db:
            # TODO: request.identity.user = admin
            admin = db.db['users']['admin']
            request.identity = Authenticator()
            request.identity.user = admin
            settings = Settings('settings', '/')
            settings.server_backend = config.get('server', 'backend')
            db.db['settings'] = settings

        objs = list(db.db['pages'].values())
        objs.extend(db.db['users'].itervalues())
        for o in objs:
            try:
                log.info("+%r", o.id)
            except Exception, e:
                import pdb; pdb.set_trace()

            for k, v in o.iteritems():
                k2 = omni(k)
                k3 = omni(v.id)
                try:
                    del o[k]
                except KeyError:
                    pass
                try:
                    del o[k2]
                except KeyError:
                    pass

                v.id = k3
                o[v.id] = v

            try:
                o.reset_items()
            except AttributeError:
                pass

            if not getattr(o, '_no_scan', None):
                objs.extend(o.values())

            f_set = set(('path', 'description', 'id', 'title', 'mime'))

            broken_content = getattr(o, 'content_name', '').endswith('.blob') and 'blobs' in getattr(o, 'content_name', '')

            for name, caster in o.editable_fields.iteritems():
                v = caster.get(o, name)
                if isinstance(v, DataBlob) and broken_content:
                    cur_data = v.open().read()
                    if not cur_data:
                        log.error("FIXING BROKEN BLOB")
                        inp = open(o.content_name, 'rb')
                        out = v.open('w')
                        sz = 2**20
                        while True:
                            data = inp.read(sz)
                            if not data:
                                break
                            out.write(data)
                        inp.close()
                        out.close()
                        os.unlink(o.content_name)
                        o.set_field(name, v)
                        o.content_name = o.title
                elif isinstance(v, Blob):
                    blob = DataBlob(v)
                    setattr(o, name, blob)
                else:
                    try:
                        o.set_field(name, v)
                        f_set.discard(name)
                    except AttributeError:
                        log.error("Could not refresh %r on %r", field, o.id)
                    except (UnicodeError, TypeError), e:
                        import pdb; pdb.set_trace()
            for field in f_set:
                try:
                    _d = getattr(o, field)
                    if isinstance(_d, basestring):
                        setattr(o, field, omni(_d))
                except AttributeError:
                    log.error("Could not set %r on %r", field, o.id)
                except (UnicodeError, TypeError), e:
                    import pdb; pdb.set_trace()

            try:
                transaction.commit()
            except ValueError:
                log.error("** cannot commit **")

        log.info("Whooshing...")
        for x in db.db['search'].rebuild():
            log.info(x.strip())

    elif len(sys.argv) == 3 and sys.argv[1] == "export":
        import datetime
        from pprint import pprint

        base = sys.argv[2]
        log.info("Exploring %s", base)

        all_obj = [ (db.db, '/') ]
        old_cwd = os.getcwd()
        for obj, obj_path in all_obj:
            log.info("-"*80)
            nbase = os.path.join(base, (obj_path or obj.path).lstrip(os.path.sep))
            try:
                os.mkdir(nbase)
            except OSError:
                pass
            log.debug("%s %s", nbase, type(obj)) #.id if hasattr(obj, 'id') else 'ROOT'
            data = obj.__dict__.copy()
            for k, v in data.iteritems():
                if isinstance(v, datetime.date):
                    data[k] = "%s/%s/%s"%(v.day, v.month, v.year)
                elif isinstance(v, DataBlob):
                    data[k] = v.filename
                    os.link(v.filename, os.path.join(nbase, data['content_name']))
                elif isinstance(v, set):
                    data[k] = list(v)
                elif k == 'owner':
                    data[k] = v.id
            if 'data' in data:
                del data['data']
            file( os.path.join(nbase, '!content_%s'%obj.__class__.__name__), 'w').write(
                dumps(data)
            )
            # recurse
            if len(obj):
                for k in obj:
                    all_obj.append((obj[k], None))
    elif len(sys.argv) == 2 and sys.argv[1] == "debug":
        from pdb import set_trace
        with db as root:
            set_trace()
    elif len(sys.argv) == 2 and sys.argv[1] == "run":
        host = config.get('server', 'host')
        port = int(config.get('server', 'port'))
        app = make_app()
        debug = (app != bottle.app())
        bottle.run(app=app, host=host, port=port, reloader=debug, server='wsgiref' if debug else config.get('server', 'backend'))

def make_app():
    global reset_required
    if not PERSISTENT_STORAGE or 'BOTTLE_CHILD' not in os.environ:
        with db as c:
            if len(c) < 3:
                reset_required = True

        if reset_required:
            init()

    # And now, http/wsgi part

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
            log.debug("Installed repoze.debug's debugging middleware")
            return app

        def dbg_werkzeug(app):
            from werkzeug.debug import DebuggedApplication
            app = DebuggedApplication(app, evalex=True)
            log.debug("Installed werkzeug debugging middleware")
            return app

        def dbg_weberror(app):
            from weberror.evalexception import EvalException
            app = EvalException(app)
            log.debug("Installed weberror debugging middleware")
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
            log.error("Unable to install the debugging middleware, current setting: %s", dbg_backend)
    # /end dbg_in_env

    #from wsgiauth.ip import ip
    #@ip
    #def authenticate(env, ip_addr):
    #    return ip_addr == '127.0.0.1'
    #
    #app = authenticate(app)

    # Let's run !
    bottle.debug(debug)
    return app
