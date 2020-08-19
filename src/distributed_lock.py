# A very simple distributed lock system. Since WSGI servers typically
# spawn more than one process, using simple thread locks won't
# suffice. We use Python multiprocessing managers for process-safeness

from multiprocessing import Lock
from multiprocessing.managers import BaseManager
import time

lock = Lock()
# dicts to store which keys are currently being used
keymap = dict()

def get_key(key):
    with lock:
        if key not in keymap:
            keymap[key] = True
            return True
        return False

def release_key(key):
    with lock:
        if key in keymap:
            del keymap[key]
            return True
        return False
    
if __name__ == '__main__':
    manager = BaseManager(('', 42875), b'tinykvmgr')
    manager.register('get_key', get_key)
    manager.register('release_key', release_key)
    server = manager.get_server()
    server.serve_forever()