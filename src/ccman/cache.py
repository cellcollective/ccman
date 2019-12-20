# imports - standard imports
import os
import os.path as osp

# imports - module imports
from   ccman.config import check_key
from   ccman.system import write, makedirs
from   ccman.util   import json as _json, crypto

import ccman

class Cache:
    def __init__(self, location = None, dirname = None):
        self.location = location or osp.expanduser("~")
        self.dirname  = dirname  or ".{name}".format(
            name = ccman.__name__
        )

    @property
    def path(self):
        path = osp.join(self.location, self.dirname)
        return path

    def exists(self):
        return osp.exists(self.path)

    def create(self, exist_ok = True):
        path = osp.join(self.location, self.dirname)
        makedirs(path, exist_ok = exist_ok)

    def set_config(self, key, value, crypt = False):
        key = check_key(key, raise_err = True)

        self.create()

        path = osp.join(self.location, self.dirname, "config.json")
        write(path, r"{}")

        if key.crypt or crypt: # pylint: disable=E1101
            value = crypto.encrypt(value)
        
        _json.update(path, { key.name: value }) # pylint: disable=E1101

    def get_config(self, key = None, default = None, check = False, crypt = False):
        path = osp.join(self.location, self.dirname, "config.json")
        
        if not osp.exists(path):
            write(path, data = r"{}")

        config = _json.read(path)

        if key:
            key    = check_key(key, raise_err = check)

            value  = config.get(key.name, default) # pylint: disable=E1101

            if value and (key.crypt or crypt): # pylint: disable=E1101
                value = crypto.decrypt(value)

            return value
        else:
            return config