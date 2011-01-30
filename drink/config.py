__all__ = ['BASE_DIR', 'config']

import os
import ConfigParser

BASE_DIR = os.path.abspath(os.path.split(__file__)[0])

config = ConfigParser.ConfigParser()

config.read([os.path.join(BASE_DIR, 'settings.ini'),
     os.path.expanduser('~/.drink.ini')])