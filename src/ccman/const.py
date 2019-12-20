# imports - standard imports
import os.path as osp

# imports - module imports
from ccman._dict import Dict

const            = Dict()
const.host.web   = "127.0.0.1"
const.port.web   = 5000
const.host.app   = "127.0.0.1"
const.port.app   = const.port.web + 1
const.host.db    = "127.0.0.1"
const.port.db    = 5432
const.host.cache = "127.0.0.1"
const.port.cache = 6379
const.host.docs  = "127.0.0.1"
const.port.docs  = 8000

const.DEPRECATED.url.development = "http://itest.cellcollective.org:8080/"
const.DEPRECATED.url.production  = "https://api.cellcollective.org/"

path           = Dict()
path.base      = osp.dirname(__file__)
path.version   = osp.join(path.base, "VERSION")
path.data      = osp.join(path.base, "data")
path.templates = osp.join(path.data, "templates")
path.patches   = osp.join(path.base, "patches.txt")
path.playbooks = osp.join(path.base, "ansible", "playbooks")