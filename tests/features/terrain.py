import logging
import mechanize
import subprocess

from lettuce import world

SERVER = 'http://localhost:5000'

bw = world.www = mechanize.Browser()
world.req = world.www.open(SERVER+'/')

if 0:
    #Log information about HTTP redirects and Refreshes.
    bw.set_debug_redirects(True)
    #Log HTTP response bodies (ie. the HTML, most of the time).
    bw.set_debug_responses(True)
    #Print HTTP headers.
    bw.set_debug_http(True)

    logger = logging.getLogger("mechanize")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

def tidy(req):
    req.seek(0)
    proc = subprocess.Popen(['tidy'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    proc.stdin.write(req.read())
    proc.stdin.close()
    ret = proc.wait()
#    print " - stdout - ".center(80)
#    print proc.stdout.read()
#    print " - stderr - ".center(80)
    if ret:
        for line in proc.stderr:
            line = line.strip()
            print line
            if not line:
                break
        raise AssertionError("Invalid HTML !")
