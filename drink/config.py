__all__ = ['BASE_DIR', 'config']

import os
import logging
import ConfigParser
log = logging.getLogger('config')

#: Base directory of drink project
BASE_DIR = os.path.abspath(os.path.split(__file__)[0])

config = ConfigParser.ConfigParser()
paths = [os.path.join(BASE_DIR, 'settings.ini'),
     os.path.expanduser('~/.drink.ini')]

log.debug("Reading config from %s", ' and '.join(paths))
config.read(paths)
