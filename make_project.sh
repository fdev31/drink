#!/bin/sh
VENV=virtualenv

echo -n "What is your python-2.x executable ? (defaults to 'python') "
read PY

if [ -z $PY ]; then
    PY=python
fi

DEST="$1"

if [ -z "$DEST" ]; then
    echo "Setups a drink virtual environment in the given folder."
    echo "Please, give a folder name as the only parameter."
    exit 1
fi

echo -n "Do you want a quick install (disables ZODB, using in memory structure) [y/N] : "
read yn

rm -fr "$DEST"

echo "DEST: $DEST"

$VENV -p $PY --no-site-packages "$DEST"

. "$DEST/bin/activate"
EPY="$DEST/bin/python"

if [ "x$yn" = "xy" ] ; then
    mv requirements.txt _requirements
    grep -vE 'ZODB|error|debug|proctitle' _requirements > requirements.txt
fi

$EPY setup.py install

if [ -f _requirements ]; then
    mv _requirements requirements.txt
fi

(cd $VIRTUAL_ENV && ./bin/drink make)

echo "Generating tarball..."
(cd `dirname "$DEST"` && tar cvf - `basename "$DEST"` | bzip2 -9 > `basename "$DEST"`.tbz) >/dev/null 2>&1


