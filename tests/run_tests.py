#!/usr/bin/env python

HTTP_PORT = 5000
HTTP_HOST = '127.0.0.1'
ADMIN = ('admin', 'admin')

import requests
import subprocess
import cookielib
import Cookie


def tidy(req):
    proc = subprocess.Popen(['tidy'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    proc.stdin.write(req.content)
    proc.stdin.close()
    ret = proc.wait()
    #print " - stdout - ".center(80)
    #print proc.stdout.read()
    #print " - stderr - ".center(80)
    if ret:
        print req.content
        for line in proc.stderr:
            line = line.strip()
            print line
            if not line:
                break
        print "FAILED(%d)"%ret#, req.status_code
    else:
        print "SUCCESS"#, req.status_code

def fetch(path, method='get', auth=None, **kw):
    if None != auth:
        #c = Cookie.SimpleCookie()
        #c['login'], c['password'] = auth
        #jar = cookielib.CookieJar()
        #jar.set_cookie(c)
        #kw['cookies'] = jar
        #auth = None
        kw = kw.copy()
        kw['auth'] = requests.AuthObject(*auth)
    if not path[0] == '/':
        path = '/'+path
    url = 'http://%s:%d%s'%(HTTP_HOST, HTTP_PORT, path)

    print kw
    method = getattr(requests, method.lower())
    return method(url, **kw)

def display(req):
    print req.status_code
    print req.headers
    print req.content


"""
r = fetch('/login', method='post', data={'login_password': 'admin', 'login_name': 'admin'})
import pdb; pdb.set_trace()
jar = cookielib.CookieJar()
cook_dict = {'login_name': 'admin', 'login_password': 'admin'}
for k, v in cook_dict.iteritems():
    c = cookielib.Cookie(1.0, k, v,
         HTTP_PORT, HTTP_PORT, HTTP_HOST, HTTP_HOST,
         '',
         '/login',
         '/login',
         'drink',
         None, # expires
         None, #discard
         '', #comment
         '', #comment url
         None, # rest
         )
    jar.set_cookie(c)

r = fetch('/pages', cookies=jar)

"""

for page in ('/', '/pages', '/groups', '/users', '/search'):
    for auth in (ADMIN, None):
        print "testing %s, auth=%r"%(page, auth)
        r = fetch(page, auth=auth)
        tidy(r)
        if r.status_code != 200:
            print "NOT OK: %d"%r.status_code
