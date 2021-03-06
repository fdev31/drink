#!/usr/bin/env python

from subprocess import Popen, PIPE
import requests
import os

def get(url, method='POST'):
    getattr(requests, method.lower())(url)

def step(cmd):
    c = Popen(cmd, stdout=PIPE, shell=isinstance(cmd, basestring))
    output = c.communicate()[0].strip()
    ret = c.returncode

    if 0 != ret:
        raise SystemExit('%r failed!\nCode: %d\n'%(cmd, v))
    print ret, cmd
    print output
    return output

# handle tag (ask, set, commit & update setup.py)
## get infos
tag = step('hg tags | grep ^0 | sort -nr | head -n 1 | cut -f1 -d " "').strip()
last_tag = [int(d) for d in tag.split('.')]
new_tag = list(last_tag)
new_tag[-1] += 1

## now, it's about strings
answer = raw_input('Current tag: %s, proposed (default): %s\nConfirm (Enter) or write version: '%(
    '.'.join(str(i) for i in last_tag),
    '.'.join(str(i) for i in new_tag)))

if answer.strip():
    # sounds crazy, here for validation:
    new_tag = '.'.join(str(int(i)) for i in answer.split('.'))
else:
    new_tag = '.'.join(str(i) for i in new_tag)

lines = []
for line in open('setup.py'):
    if line.strip().startswith('version'):
        left, right = line.split('=')
        lines.append('%s="%s",\n'%(left, new_tag))
    else:
        lines.append(line)

# Update README.rst file with README.md content
# setting drink version at the same time
step('markdown README.md -e utf-8 | sed "s/DRINK_VERSION/%s/g" | ./html2rst.py > drink_defaults%sREADME.rst'%(new_tag, os.path.sep)
readme = open(os.path.join('drink_defaults', 'README.rst')).read()

if 'DEBUG' in os.environ:
    raise SystemExit()
else:
    raw_input('LAST CHANCE TO QUIT, PRESS ENTER TO CONTINUE'.center())

## update setup.py according to new tag & commit this version
open('setup.py', 'w').writelines(lines)
#TODO: replace Hg commands with mercurial module
step(['hg', 'ci', '-m', 'Prepare version %s'%new_tag, 'setup.py', os.path.join('drink_defaults', 'README.rst')])
## Note version & tag it
uuid = step('hg id -i').rstrip('+ ')
print uuid, ">", new_tag
step('hg tag %s'%new_tag)
# push code
step('hg push')
step('hg push hub') # git+ssh://git@github.com:fdev31/drink.git
step('hg push bit') # https://fab31@bitbucket.org/fab31/drink

# publish
get('http://readthedocs.org/build/636') # readthedocs hook
step('python ./setup.py sdist upload')

