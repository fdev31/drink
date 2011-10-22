#!/bin/sh
# Nginx configuration:
# 
#  upstream bottle {
#    # Distribute requests to servers based on client IP. This keeps load
#    # balancing fair but consistent per-client. In this instance we're
#    # only using one uWGSI worker anyway.
#    ip_hash;
#    server unix:/tmp/uwsgi.sock;
#  }
#
#
#        location / {
#	      uwsgi_pass  bottle;
#	      include     uwsgi_params;
#	}

# In venv, add  -H /path/to/py/home

P=
H=
cd ${H}

http='--http 127.0.0.1:5000'
sock='-s /tmp/uwsgi.sock -C 666'

zeoctl -C database/zeo.conf start

exec uwsgi -p 10 $sock $http --module 'drink:make_app()'
