# imports - standard imports
import os.path as osp

# imports - module imports
from   ccman.system import makedirs
import ccman

def run(*args, **kwargs):
    bench = kwargs.get("bench")
    for site in bench.sites:
        path = osp.join(site.path, "backups")
        makedirs(path, exist_ok = True)