#!/usr/bin/env python
import os
import sys

try:
    import setproctitle
except ImportError:
    print "Unable to set process' name, easy_install setproctitle, if you want it."
else:
    setproctitle.setproctitle('drink')


if __name__ == "__main__":
    sys.path.insert(0, os.path.curdir)
    import bottle
    app = bottle.app()
    from drink import init, db
    from drink.config import config

    if len(sys.argv) == 2 and sys.argv[1] == "init":
        init()
        db.db.pack()
    # TODO: rename __init_
    # TODO: create "update" command
    elif len(sys.argv) == 2 and sys.argv[1] == "pack":
        db.db.pack()
    else:
        host = config.get('server', 'host')
        port = int(config.get('server', 'port'))
        mode = config.get('server', 'backend')

        # handle debug mode
        debug = False
        if 'DEBUG' in os.environ:
            mode = 'debug'
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

        #from wsgiauth.ip import ip
        #@ip
        #def authenticate(env, ip_addr):
        #    return ip_addr == '127.0.0.1'
        #
        #app = authenticate(app)

        # Let's run !
        try:
            bottle.debug(debug)
            bottle.run(app=app, host=host, port=port, reloader=debug, server='wsgiref' if mode == 'debug' else mode)
        finally:
            db.db.pack()
