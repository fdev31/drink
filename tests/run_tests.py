#!/usr/bin/env python

import urllib
import urllib2
import subprocess

cook_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
urllib2.install_opener(cook_opener)

values = {'login_name': 'admin', 'login_password': 'admin'}

def request(url, data=None, **kw):
    if isinstance(data, dict):
        data = urllib.urlencode(data)
    return urllib2.urlopen( urllib2.Request('http://localhost:5000'+url, data) )

def tidy(req):
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
        print "FAILED(%d)"%ret#, req.status_code
    else:
        print "SUCCESS"#, req.status_code

# Not logged-in
tidy( request('/pages') )
tidy( request('/search') )
tidy( request('/users') )

# Logged-in
tidy( request('/login', values) )
tidy( request('/pages') )
tidy( request('/search') )
tidy( request('/users') )

