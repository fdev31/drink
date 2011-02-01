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
            # debug middleware loading
            try:
                from repoze.debug.pdbpm import PostMortemDebug
            except ImportError:
                try:
                    from werkzeug.debug import DebuggedApplication
                except ImportError:
                    try:
                        from weberror.evalexception import EvalException
                    except ImportError:
                        print "Unable to install the debugging middleware, consider installing werkzeug or weberror."
                        debug = False
                    else:
                        app = EvalException(app)
                        print "Installed weberror debugging middleware"
                else:
                    app = DebuggedApplication(app, evalex=True)
                    print "Installed werkzeug debugging middleware"
            else:
                app = PostMortemDebug(app)
                print "Installed repoze.debug's debugging middleware"

        #from wsgiauth.ip import ip
        #@ip
        #def authenticate(env, ip_addr):
        #    return ip_addr == '127.0.0.1'
        #
        #app = authenticate(app)

        # Let's run !
        try:
            bottle.debug(debug)
            bottle.run(app=bottle.app(), host=host, port=port, reloader=debug, server='wsgiref' if mode == 'debug' else mode)
        finally:
            db.db.pack()
