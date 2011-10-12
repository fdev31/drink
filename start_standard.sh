#!/bin/sh
P=
H=

cd ${H}

zeoctl -C database/zeo.conf start

exec $P ./manage run
