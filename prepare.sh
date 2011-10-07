#!/bin/sh
VENV=virtualenv
PY=python

DEST="$1"

if [ -z "$DEST" ]; then
    echo "Please, give a name as the only parameter"
    exit 1
fi

rm -fr "$DEST"

$VENV -p $PY --no-site-packages "$DEST"

source "$DEST/bin/activate"
cp -r . "$DEST/drink"
"$DEST/bin/pip" install -r requirements.txt
(cd `dirname "$DEST"` && tar cvf - `basename "$DEST"` | bzip2 -9 > `basename "$DEST"`.tbz)

