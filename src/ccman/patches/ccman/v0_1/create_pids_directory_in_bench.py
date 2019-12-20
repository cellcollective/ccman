# imports - standard imports
import os.path as osp

# imports - module imports
from   ccman.system import makedirs
import ccman

def run(*args, **kwargs):
    bench = kwargs.get("bench")
    path  = osp.join(bench.path, "pids")
    makedirs(path, exist_ok = True)