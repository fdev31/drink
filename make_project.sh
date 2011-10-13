#!/bin/sh
VENV=virtualenv
PY=python

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

cp -r drink "$DEST/drink"
cp -r scss "$DEST/scss"
mkdir -p "$DEST/database/cache"
mkdir -p "$DEST/database/blobs"
cp database/*.conf "$DEST/database/"

if [ "x$yn" = "xy" ] ; then
    grep -vE 'ZODB|error|debug|proctitle' requirements.txt > requirements_test.txt
    $DEST/bin/pip install -r requirements_test.txt
else
    $DEST/bin/pip install -r requirements.txt
fi

for script in manage start_standard.sh start_uwsgi.sh; do
    sed -e "s#^P=\$#P=../bin/python#" -e "s#^H=\$#H=$DEST/drink/#" < "$script" > "$DEST/$script"
done

echo "Generating tarball..."
(cd `dirname "$DEST"` && tar cvf - `basename "$DEST"` | bzip2 -9 > `basename "$DEST"`.tbz) >/dev/null 2>&1


