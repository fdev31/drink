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

$VENV -p $PY --no-site-packages "$DEST"

source "$DEST/bin/activate"
cp -r . "$DEST/drink"

if [ "$yn" == "y" ]; then
    grep -vE ZODB|error|debug requirements.txt > requirements_test.txt
    "$DEST/bin/pip" install -r requirements_test.txt
else
    "$DEST/bin/pip" install -r requirements.txt
fi
for script in start_standard.sh start_uwsgi.sh; do
    sed -e "s/P=/P=../bin/python" -e "s/H=/H=$DEST/drink/" < "$DEST/drink/$script" > "$DEST/$script"
done

(cd `dirname "$DEST"` && tar cvf - `basename "$DEST"` | bzip2 -9 > `basename "$DEST"`.tbz)

