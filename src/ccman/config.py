# imports - compatibility imports
from six import string_types

# imports - standard imports
import os
import json
import collections

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.bench.util  import _check_bench
from   ccman.util.crypto import generate_hash, decrypt
from   ccman.util.types  import merge_dict

_VALID_KEYS = [
    ccman.Dict({ "name": "gitlab_token", "crypt": True }),
    ccman.Dict({ "name": "slack_api_token", "crypt": True }),

    "web_host",
    "web_port",
    "cache_host",
    "cache_port",
    "app_host",
    "app_port",

    "database_directory",
    "database_host",
    "database_port",
    "default_site",

    "database_name",
    "database_username",
    "database_password",

    "jupyter_notebook_ip",
    "jupyter_notebook_password",
    "jupyter_notebook_open_browser",
    "jupyter_notebook_port",

    "test_config",
    ccman.Dict({ "name": "test_crypt_config", "crypt": True }),

    "benches"
]

def check_key(key, raise_err = False):
    default = ccman.Dict({ "crypt": False })

    check   = None

    for k in _VALID_KEYS:
        if isinstance(k, collections.Mapping):
            if k.name == key: # pylint: disable=E1101
                check = k
        else:
            if k == key:
                check = merge_dict(default, { "name": k })

        if check:
            break

    if not check:
        if raise_err:
            raise ccman.KeyError("{key} not a valid key.".format(
                key = key
            ))
        else:
            check = False

    return check

def get_config(key = None, default = None, check = False, path = None, prompt = None, crypt = False, global_ = False):
    """
    Get Config
    """
    path = path or os.getcwd()
    path = _check_bench(path, raise_err = False, search_parent_directories = True)

    if key:
        key   = check_key(key, raise_err = check)

        value = None

        if path:
            bench = ccman.Bench(path)
            value = bench.get_config(key.name, default, check = check, crypt = key.crypt or crypt)

        if not value:
            value = ccman.cache.get_config(key.name, default, check = check, crypt = key.crypt or crypt)

        if not value and prompt:
            prompt = prompt if isinstance(prompt, string_types) else key.name  
            value  = click.prompt(prompt)

            if global_:
                ccman.cache.set_config(key.name, value, crypt = key.crypt or crypt)
            else:
                if path:
                    bench = ccman.Bench(path)
                    bench.set_config(key.name, value, crypt = key.crypt or crypt)

        return value
    else:
        config = ccman.cache.get_config()
        local  = dict()

        if path:
            bench = ccman.Bench(path)
            local = bench.get_config()

        config.update(local)

        return config