#!/bin/sh
P=
H=

if [ -n "$H" ]; then
    cd ${H}
fi

zeoctl -C database/zeo.conf start

exec $P ./manage run
