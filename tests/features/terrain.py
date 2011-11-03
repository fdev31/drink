from lettuce import world
import logging
import subprocess
import webtest
import os, sys
sys.path.insert(0, os.pardir)
import drink

world.www = webtest.TestApp(drink.make_app())
VERBOSE=False

import os
#from lettuce import after

#@after.each_step
#def apply_pdb_if_not_in_ciserver(step):
#    if 'CI_SERVER' in os.environ:
#        return
#
#    has_traceback = step.why
#
#    if not has_traceback:
#        return
#
#    import pdb
#
#    matched, defined = step.pre_run(False)
#
#    if matched:
#        args = matched.groups()
#        kwargs = matched.groupdict()
#        pdb.runcall(defined.function, step, *args, **kwargs)

def tidy(html):
    proc = subprocess.Popen(['tidy'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    proc.stdin.write(html)
    proc.stdin.close()
    ret = proc.wait()
#    print " - stdout - ".center(80)
#    print proc.stdout.read()
#    print " - stderr - ".center(80)
    if ret:
        contains_error = False
        for line in proc.stderr:
            if VERBOSE:
                print line,

            if not contains_error and 'were found' in line and 'error' in line:
                contains_error = ' 0 error' not in line

        if contains_error:
            raise AssertionError("Invalid HTML !")
