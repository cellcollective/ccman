# imports - standard imports
import os
import os.path as osp

# imports - module imports
from ccman.__attr__  import (
    __name__,
    __version__,
    __build__,
    __author__,
    __description__,
    get_version_str
)
from ccman._dict       import Dict
from ccman.const       import const, path
from ccman.bench       import Bench
from ccman.bench.site  import Site
from ccman.bench.util  import _check_bench
from ccman.cache       import Cache
from ccman.exception   import *
from ccman.logger      import log
from ccman.template    import render_template
from ccman.environment import getenv, setenv
from ccman.queue       import enqueue
from ccman.db          import connect as db_connect

cache  = Cache()
cache.create()

# patch
_bench = _check_bench(os.getcwd(), search_parent_directories = True)
if _bench:
    _bench = Bench(_bench)

db     = db_connect("sqlite:///%s/db.db" % cache.path, bootstrap = True)

from ccman.config import get_config
from ccman import gitlab, system, util

# patch
_benches = get_config("benches", [ ])
for _path in _benches:
    if not _check_bench(_path):
        updated = [p for p in _benches if p != _path]
        cache.set_config("benches", updated)
_benches = [Bench(_path) for _path in get_config("benches", [ ])]