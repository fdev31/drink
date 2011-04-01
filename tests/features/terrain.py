from lettuce import world
import mechanize
import subprocess

SERVER = 'http://localhost:5000'

world.www = mechanize.Browser()
world.req = world.www.open(SERVER+'/')

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
