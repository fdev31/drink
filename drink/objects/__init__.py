from __future__ import absolute_import
from drink.config import config

__all__ = ['classes', 'get_object', 'init']

classes = {}

objects_to_load = [k for k, v in config.items('objects')]

def get_object(current, objpath):

    path_list = [p for p in objpath.split('/') if p]
    last_idx = len(path_list) - 1
    for i, elt in enumerate(path_list):

        if i == last_idx:
            try:
                current = current[elt]
            except (KeyError, AttributeError, TypeError):
                try:
                    current = getattr(current, elt)
                except AttributeError:
                    raise AttributeError(elt)
            break # found a matching object
        else:
            try:
                current = current[elt]
            except (KeyError, AttributeError):
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


    del exported
