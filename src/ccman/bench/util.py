# imports - standard imports
import os.path as osp
import subprocess
import time

# imports - third-party imports
import redis

# imports - module imports
from   ccman.ansible import Playbook
from   ccman.system  import which, pardir, check_port_available, popen
import ccman

_BENCH_TREE = \
{
       "logs": None,
    "configs": None,
      "sites": None,
       "data": None
}

_SITE_TREE  = \
{
     "public": None,
    "backups": None
}

_REDIS_CONNECTION = None

def _get_yarn():
    yarn = "yarn" # which('yarn') fails on Windows?

    return yarn

def _get_nginx_path():
    paths = [
        "/usr/local/nginx",
        "/etc/nginx",
        "/usr/local/etc/nginx"
    ]

    for path in paths:
        if osp.exists(path):
            return path
    
    raise ccman.ValueError("nginx path not found.")

def _get_systemd_path():
    paths = [
        "/etc/systemd/system"
    ]

    for path in paths:
        if osp.exists(path):
            return path

    raise ccman.ValueError("systemd path not found.")

def _check_bench(name, raise_err = False, search_parent_directories = False):
    path  = osp.realpath(name)
    check = path

    if not osp.exists(path):
        if raise_err:
            raise ccman.ValueError("{name} does not exists.".format(
                name = name
            ))
        else:
            check = None

    if check:
        dirpar = pardir(path)
            
        for directory in list(_BENCH_TREE):
            dirpath = osp.join(path, directory)
            if not osp.exists(dirpath):
                if raise_err:
                    if search_parent_directories and path != dirpar:
                        check = None
                        break
                    else:
                        raise ccman.ValueError("Not a valid Bench.".format(
                            path = path
                        ))
                else:
                    check = None
                    break

        if not check and search_parent_directories and path != dirpar:
            check = _check_bench(dirpar, raise_err = raise_err,
                search_parent_directories = search_parent_directories)

    return check

def _check_site(name, raise_err = False):
    path  = osp.realpath(name)
    check = path

    ccman.log().info("Checking Site {name}".format(name = name))

    if not osp.exists(path):
        if raise_err:
            raise ccman.ValueError("{name} does not exists.".format(
                name = name
            ))
        else:
            check = None
        
    return check

def _get_available_port(port, host = "127.0.0.1"):
    paths = ccman.get_config("benches", [ ])
    taken = [ ]

    for path in paths:
        bench  = ccman.Bench(path)
        taken += list(bench.port.values())
    
    while port in taken or not check_port_available(port, host = host):
        port = port + 1
    
    return port

def get_redis_connection(host = ccman.const.host.cache, port = ccman.const.port.cache, refresh = False, raise_err = True):
    global _REDIS_CONNECTION

    if not _REDIS_CONNECTION or refresh:
        _REDIS_CONNECTION = redis.StrictRedis(host = host, port = port)

        try:
            _REDIS_CONNECTION.ping()
        except Exception:
            _REDIS_CONNECTION = None
            
            if raise_err:
                raise

    return _REDIS_CONNECTION