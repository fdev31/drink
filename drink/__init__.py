from __future__ import absolute_import, with_statement
"""
Drink!

"""
__all__ = ['get_object',
 'classes',
 'add_upload_handler',
 'request', 'response',
 'Page', 'ListPage'
 'omni', 'bytes2human',
 'db', 'unauthorized',
 'make_app', 'init']
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
import bottle
from hashlib import sha1

#: All kind of drink objects as a ``{"name": Page_class}`` mapping.

classes = {}
if config.get('server', 'templates'):
    bottle.TEMPLATE_PATH.append(config.get('server', 'templates').strip())
bottle.TEMPLATE_PATH.append(os.path.join(BASE_DIR, 'templates'))
STATIC_PATH = config.get('server', 'static_folder') or os.path.abspath(os.path.join(BASE_DIR, "static"))
BASE_DIR = os.path.dirname(STATIC_PATH.rstrip(os.path.sep))
import drink_defaults
DEFAULTS_DIR = os.path.dirname(drink_defaults.__file__)
ORIG_DB_PATH = os.path.abspath(os.path.join(DEFAULTS_DIR, 'database'))

DB_PATH = config.get('server', 'database') or ORIG_DB_PATH
if not DB_PATH.endswith(os.sep):
    DB_PATH += os.sep


# auto-guess & set datadir in case of inchanged default
log.debug("Using DB informations from %s", DB_PATH)
def _fix_datadir(txt, zeo_fname=None):
    try:
        i = txt.index('%define DATADIR database\n')
    except ValueError:
        i = -1
    if i >= 0:
        txt[i] = '%%define DATADIR %s\n'%DB_PATH
    if zeo_fname:
        for idx, line in enumerate(txt):
            if ' zeo.conf' in line:
                txt[idx] = line.replace("zeo.conf", zeo_fname)
    return ''.join(txt)

try:
    DB_CONFIG = _fix_datadir(open(os.path.join(DB_PATH, "zodb.conf")).readlines())
except IOError:
    import shutil
    try:
        os.makedirs(os.path.join(DB_PATH, 'blobs'))
        os.makedirs(os.path.join(DB_PATH, 'cache'))
    except OSError:
        pass
    shutil.copy( os.path.join(ORIG_DB_PATH, 'zodb.conf'), os.path.join(DB_PATH, 'zodb.conf'))
    shutil.copy( os.path.join(ORIG_DB_PATH, 'zeo.conf'), os.path.join(DB_PATH, 'zeo.conf'))
    shutil.copy( os.path.join(ORIG_DB_PATH, 'blobs', '.layout'), os.path.join(DB_PATH, 'blobs', '.layout'))
    DB_CONFIG = _fix_datadir(open(os.path.join(DB_PATH, "zodb.conf")).readlines())

# Import main modules used + namespace setup

# http
from bottle import route, static_file, request, response, redirect as rdr, abort
# templating
from urllib import unquote

#: A json serialization function
dumps = bottle.JSONPlugin().json_dumps

def bytes2human(num):
    ''' Converts an integer or float value to human-readable string

    :arg num: Number of bytes
    :type num: `int` or `float`
    :returns: a short display string containing the value + the "best fitting" unit
    :rtype: `unicode`
    '''
    for u in ('k', 'M', 'G'):
        num /= 1000.0
        if num < 951:
            break
    return u'%.1f %s'%(num, u)

def omni(txt):
    ''' Converts any text form to unicode text

    :arg txt: the "unknown state" text
    :type txt: `unicode` or `str`
    :returns: an "http" unquoted unicode string
    :rtype: `unicode`
    '''
    if isinstance(txt, unicode):
        return txt
    else:
        txt = unquote(txt)
        try:
            return txt.decode('utf-8')
        except UnicodeError:
            return txt.decode('latin1')

def init():
    """ Re-initialize drink's database """
    from drink.objects.finder import reset
    reset()
    with db as root:
        root.clear()
        transaction.commit()

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
            try:
                root[pagename] = classes[ name ](pagename, '/')
            except Exception, e:
                log.error('Unable to create %r element with type %r (%r)\nexpect problems, try to enable this object type next time.'%(pagename, name, e))

        mdown = classes['Web page (markdown)']('help', '/pages/')
        help = os.path.abspath(os.path.join(DEFAULTS_DIR, "HELP.md"))
        mdown.content = open(help).read()
        mdown.owner = admin
        mdown.min_rights = 'r'
        root['pages']['help'] = mdown

# Setup db
reset_required = False
try:
    from .zdb import Database, DataBlob, Model, transaction
    PERSISTENT_STORAGE = True
    log.info("Enabling persistent storage, using ZODB")
except ImportError:
    log.warning("Not enabling persistent storage, using dumb db")
    PERSISTENT_STORAGE = False
    from .dumbdb import Database, DataBlob, Model, transaction

#: The database object, prefer using :func:`drink.get_object` instead

db = Database(bottle.app(), DB_CONFIG)

# Load Basic objects
from .objects.generic import Page, ListPage, Settings, default_view
from .objects import classes as obj_classes, get_object, init as init_objects

def add_upload_handler(ext, obj_name):
    """ Add an opload handler into drink upload system

    :arg ext: extension to register
    :type ext: `str` or `list` of `str`
    :arg obj_name: object name, will be looked up via :obj:`drink.classes`
    :type obj_name: `str`
     """

    if isinstance(ext, basestring):
        ext = [ext]
    for e in ext:
        Page.upload_map[e] = obj_name

# Finally load all the objects
init_objects()
classes.update(obj_classes)
del init_objects, obj_classes

def unauthorized(message='Action NOT allowed', code=401):
    ''' Returns proper value to indicate the user has no access to this ressource

    :arg message: Message to show to the user
    :type message: `unicode` or `str`
    :arg code: HTTP error code, defaults to ``401``
    :type code: int
    '''
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
                log.warning("* Trying %s"%sa.__name__)
                return sa(self.host, self.port, **self.options).run(handler)
            except ImportError:
                pass

bottle.server_names['drink'] = DrinkServer

# Real code starts here

class Authenticator(object):
    """ Authentication class, handles user's identity """

    __slots__ = ['user', 'success', 'session', 'groups', 'admin', 'id']

    def __init__(self):
        self.session = session = bottle.request.environ.get('beaker.session')
        logged_in = session.get('logged_in', '')
        if logged_in:
            self.user = db.db['users'][session['login']]
            ok = self.user.password == logged_in
            if not ok:
                self.user = None
            self.success = ok
        else:
            self.success = False

        if self.success:
            #: set of current user's groups
            self.groups = self.user.groups.copy()
            self.groups.add('users')
            #: is the user an admin ?
            self.admin = 'admin' in self.groups or self.user.id == 'admin'
        else:
            self.user = db.db['users']['anonymous']
            self.admin = False
            self.groups = set()

        self.groups.add('anonymous')

        #: `id` of the user (same as :obj:`.user.id`)
        self.id = self.user.id

    def access(self, obj):
        """ Returns a string describing possible access to `obj`

        :arg obj: the object you want to inspect access
        :type obj: any Drink-stored object
        :returns: a string componed of single-letter symbols
        :rtype: str

        String is a combination of:
            :o: owner
            :w: write
            :r: read
            :a: add / append
            :t: traverse (access sub-content but don't imply read access)
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
        a = 15552000 # 6*30*24*60*60
        session = request.identity.session
        session['logged_in'] = sha1(request.forms.get('login_password', '')).hexdigest()
        session['login'] = request.forms.get('login_name', '')
        session.save()
        return rdr(request.params.get('from', '/'))
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
        return default_view(db.db['pages'], page='main.html', html=html, classes={}, no_auth=True)


@route("/logout", method=['GET', 'POST'])
def log_out():
    session = bottle.request.environ.get('beaker.session')
    session['logged_in'] = ''
    return rdr('/')

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
                return rdr(omni(o['redirect']).encode('utf-8'))
            if 'error' in o:
                return abort(o['code'], o['message'])
        response.content_type = "application/json"
        return dumps(o)
    elif hasattr(o, 'drink_name'): # isinstance(o, 'Model') but more implicit
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
    """ Starts drink application """
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
    make    : make a new drink project
    start   : start all required servers
    run     : starts the server
    db      : starts the database server
    stopdb  : stops the database server
    init    : reset database
    pack    : pack database (more compact/faster)
    rebuild : EXPERIMENTAL, will try to convert & clean an old database to newer format
    export  : EXPERIMENTAL, will try to dump all the data into the given folder
    debug   : run a debugger after loading
    help    : this help :)

Without any argument, it will just run the server.
if DEBUG environment variable is set, it will start in debug mode.
        """
    elif len(sys.argv) == 2 and sys.argv[1] == "init":
        init()
        db.pack()
    elif len(sys.argv) == 2 and sys.argv[1] in ("run", "db", "start"):
        if sys.argv[1] != "run":
            fname = os.path.join(DB_PATH, 'zeo.conf')
            log.debug('fixing %r', fname)
            new_conf = _fix_datadir(open(fname).readlines(), fname)
            open(fname, 'w').write(new_conf)
            cmd = 'zeoctl -C %s start'%(fname)
            os.system(cmd)
        if sys.argv[1] != "db":
            host = config.get('server', 'host')
            port = int(config.get('server', 'port'))
            app = make_app(full=True)
            debug = (app != bottle.app())
            bottle.run(app=app, host=host, port=port, reloader=debug, server='wsgiref' if debug else config.get('server', 'backend'))
    elif len(sys.argv) == 2 and sys.argv[1] == "stopdb":
        cmd = "zeoctl -C %s stop"%os.path.join(DB_PATH, 'zeo.conf')
        print(cmd)
        os.system(cmd)
    elif len(sys.argv) == 2 and sys.argv[1] == "make":
        def inp(txt):
            return raw_input(txt+': ').strip()

        import shutil
        import drink
        import drink_defaults

        fold = inp('Project folder')

        if os.path.exists(fold):
            shutil.rmtree(fold)

        # fresh copy
        os.mkdir(fold)

        fold = os.path.abspath(fold)

        for project_fold, subs in (
            [ os.path.dirname(drink_defaults.__file__), None],
            [ os.path.join(os.path.dirname(drink.__file__)), ['static', 'templates']],
            ):
            for src in subs or os.listdir(project_fold):
                f = os.path.join(project_fold, src)
                if os.path.isdir(f):
                    if fold.endswith('_'):
                        os.symlink(f, os.path.join(fold, src))
                    else:
                        shutil.copytree(f, os.path.join(fold, src))

        cust = inp('Additional python package with drink objects\n(can contain dots)')
        host = inp('Ip to use (just ENTER to allow all)') or '0.0.0.0'
        port = inp('HTTP port number (ex: "80"), by default %s:5000 will be used'%host) or '5000'
        print "Objects to activate:"
        objs = [
            ('a gtd-like tasklist', 'tasks'),
            ('a wiki-like web page in markdown format', 'markdown'),
            ('a tool to find objects in database', 'finder'),
            ('a filesystem proxy, allow sharing of arbitrary folder or static websites', 'filesystem'),
        ]
        objects = []
        for o in objs:
            #ans = inp('Activate %s, %s (y/N)'%(o[1], o[0]))
            ans = 'y'
            print("%s : %s"%(' - '.join(o), ans))
            if ans.lower() == 'y':
                objects.append(o[1]+'=')

        layout = []
        k = classes.keys()
        while True:
            name = inp('Additional root item name (just ENTER to finish)')
            if not name:
                break
            for i, n in enumerate(k):
                print "%2d - %s"%(i, n)
            idx = int(inp('Select the desired type index'))
            layout.append('%s = %s'%(name, k[idx]))
        conf = """[server]
database = %s%sdatabase
objects_source = %s
templates = %s
static_folder = %s
host = %s
port = %s


[objects]
%s

[layout]
pages = Folder index
search = Finder
%s
"""%(fold, os.path.sep, cust,
        os.path.abspath(os.path.join(fold, 'templates')),
        os.path.abspath(os.path.join(fold, 'static')),
        host, port,
        '\n'.join(objects),
        '\n'.join(layout),
        )
        open( os.path.join(fold, 'drink.ini'), 'w' ).write(conf)
        conf = """#!/bin/sh
SOCK_DIR="/tmp"
cat << EOF
Example of nginx configation:
upstream drink {
    ip_hash;
    server unix:${SOCK_DIR}/uwsgi.sock;
}
location / {
    uwsgi_pass drink;
    include uwsgi_params;
}
EOF

if [ ! -z "$VIRTUAL_ENV" ] ; then
    export PYTHONHOME=$VIRTUAL_ENV
fi

export PYTHONPATH="${PWD}:%(proj)s:${PYTHONPATH}"

cd "%(proj)s"

http='--http %(host)s:%(port)s'
sock="-s ${SOCK_DIR}/uwsgi.sock -C 666"
stats="--stats ${SOCK_DIR}/stats.socket"
stats='' # disable stats

zeoctl -C database/zeo.conf start

exec uwsgi -p 1 $sock $http $stats --module 'drink:make_app()'
"""%dict(proj=fold, host=host, port=port)
        open( os.path.join(fold, 'start_uwsgi'), 'w' ).write(conf)
        os.chmod(os.path.join(fold, 'start_uwsgi'), 0777)
        if cust.strip():
            try:
                __import__(cust)
            except ImportError:
                cust_dir = os.path.join(fold, cust.strip())
                os.mkdir(cust_dir)
                open(os.path.join(cust_dir, '__init__.py'), 'w')
        print """Project created successfuly.

You can now go into the %s folder and run

- drink db (to start the database daemon)
- drink run (to start the web server)

If you run with DEBUG=1 in environment, templates and python code should reload automatically when changed.
For static files changes, no restart is needed.
        """%fold
    elif len(sys.argv) == 2 and sys.argv[1] == "pack":
        from drink.objects import finder
        finder.init()
        finder.indexer.optimize()
        db.pack()
        print "packed."
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

from beaker.middleware import SessionMiddleware

def make_app(full=False):
    """ Returns Drink WSGI application """
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

    if full and mode not in ('debug', 'paste', 'rocket'):
        try:
            import gevent.monkey
            gevent.monkey.patch_all()
        except ImportError:
            async = False
        else:
            log.warning('Using gevent for asynchronous processing')
            async = True

    config.async = async

    app = bottle.app()
    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires': 300,
        #'session.data_dir':  DB_PATH,
        'session.auto': True
    }
    app = SessionMiddleware(app, session_opts)

    if not full:
        return app

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
