__all__ = ['BASE_DIR', 'config']

import os
import logging
import ConfigParser
log = logging.getLogger('config')

#: Base directory of drink project
BASE_DIR = os.path.abspath(os.path.split(__file__)[0])

#: Drink configuration object, which is a :class:`ConfigParser.ConfigParser` instance reading into user directory and current folder's drink.ini file

config = ConfigParser.ConfigParser()

paths = [os.path.join(BASE_DIR, 'settings.ini'),
     os.path.expanduser('~/.drink.ini'),
     os.path.join(os.getcwd(), 'drink.ini'),
     ]

log.debug("Reading config from %s", ' and '.join(paths))
config.read(paths)
