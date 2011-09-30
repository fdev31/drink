from __future__ import absolute_import
from drink.config import config
import drink
from drink import request
from urllib import unquote

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

    path_list = [unquote(p).decode('utf-8') for p in objpath.split('/') if p]
    last_idx = len(path_list) - 1
    for i, elt in enumerate(path_list):
        if elt[0] in '._':
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
                if elt.startswith('_'):
                    if not no_raise:
                        return drink.unauthorized('Not authorized')
                    return
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
    for obj in objects_to_load:
        print "[Loading %s]"%obj
        try:
            exec('from . import %s as _imported'%obj)
        except Exception:
            print "Unable to load %s, remove it from config file in [objects] section."%obj
            raise
        else:
            for _child in dir(_imported):
                klass = getattr(_imported, _child)
                exported_name = getattr(klass, 'drink_name', None)
                if exported_name:
                    if exported_name in classes:
                        raise ValueError('Duplicate object: %s !! provided by %r and %r'%(exported_name, classes[exported_name], _imported))
                    else:
                        print "  - %s loaded"% exported_name
                        classes[exported_name] = klass
