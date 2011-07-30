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
            drink.unauthorized('Not authorized (forbidden character)')
        if i == last_idx:
            # getting
            try:
                current = current[elt]
                if 'r' not in drink.request.identity.access(current):
                    if not no_raise:
                        drink.unauthorized('Not authorized')
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
                        drink.unauthorized('Not authorized')
                    return
                current = current[elt]
                if 't' not in drink.request.identity.access(current):
                    if not no_raise:
                        drink.unauthorized('Not authorized')
                    return
            except (KeyError, AttributeError):
                if no_raise:
                    return
                raise AttributeError(elt)
    return current

def init():
    for obj in objects_to_load:
        try:
            exec('from .%s import exported'%obj)
            classes.update(exported)
        except Exception:
            print "Unable to load %s, remove it from config file in [objects] section."%obj
            raise
