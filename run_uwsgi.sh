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

http='--http 127.0.0.1:5000'
sock='-s /tmp/uwsgi.sock -C 666'

exec uwsgi -p 1 $sock $http --module 'drink:make_app()'
