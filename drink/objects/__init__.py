from __future__ import absolute_import
from drink.config import config
import logging
import drink
import sys
from drink import request
from urllib import unquote
log = logging.getLogger('objects')

__all__ = ['classes', 'get_object', 'init']

class _AuthDict(dict):
    def iterkeys(self):
        adm = request.identity.admin
        return (k for k in dict.iterkeys(self) if not self[k].hidden_class or adm)

    def keys(self):
        return list(self.iterkeys())

classes = _AuthDict()

objects_to_load = [k for k, v in config.items('objects')]

def get_object(current, objpath, no_raise=False):
    """ Fetch an object from database, looking at permissions to approve

    :arg current: root object to browse for childrens
    :type current: :class:`drink.Page`
    :arg objpath: path to the children
    :type objpath: str
    :arg no_raise: (optional) don't raise exceptions
    :type no_raise: `bool`
    """

    path_list = [drink.omni(p) for p in objpath.split('/') if p]
    last_idx = len(path_list) - 1
    for i, elt in enumerate(path_list):
        if elt[0] in '._' and  elt != '_static':
            return drink.unauthorized('Not authorized (forbidden character)')
        if i == last_idx:
            # getting
            try:
                current = current[elt]
                if 'r' not in drink.request.identity.access(current):
                    if not no_raise:
                        return drink.unauthorized('Not authorized')
                    return
            except (KeyError, AttributeError, TypeError):
                try:
                    current = getattr(current, elt)
                except AttributeError:
                    if not no_raise:
                        raise AttributeError(elt)
                    return
            break # found a matching object
        else:
            # traversal
            try:
                current = current[elt]
                if 't' not in drink.request.identity.access(current):
                    if not no_raise:
                        return drink.unauthorized('Not authorized')
                    return
            except (KeyError, AttributeError):
                if no_raise:
                    return
                raise AttributeError(elt)
    return current

def init():
    """ Load all objects.
    Reads configuration `objects_source` from [server].
    Objects to load are read at module loading time from the [objects] section
    """
    altern_source = config.get('server', 'objects_source')
    sys.path.insert(0, drink.BASE_DIR)

    log.debug('Trying to load: %s from %r'%(', '.join(objects_to_load), altern_source))
    for obj in objects_to_load:
        log.info("[Loading %s]", obj)
        try:
            exec('from %s import %s as _imported'%(altern_source, obj))
        except ImportError:
            try:
                exec('from . import %s as _imported'%obj)
            except Exception:
                log.error("Unable to load %s, remove it from config file in [objects] section.", obj)
                continue

        for _child in dir(_imported):
            klass = getattr(_imported, _child)
            exported_name = getattr(klass, 'drink_name', None)
            if exported_name:
                if exported_name in classes:
                    raise ValueError('Duplicate object: %s !! provided by %r and %r'%(exported_name, classes[exported_name], _imported))
                else:
                    log.info("  - %s loaded"% exported_name)
                    classes[exported_name] = klass

