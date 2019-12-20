import sys
import os, os.path as osp
import datetime as dt

def pardir(path, level = 1):
    for _ in range(level):
        path = osp.dirname(path)
    return path

BASEDIR = osp.realpath(pardir(__file__, 2))
NOW     = dt.datetime.now()

sys.path.insert(0, BASEDIR)

import ccman

project   = ccman.__name__
author    = ccman.__author__
copyright = "%s %s" % (NOW.year, ccman.__author__)

version   = ccman.__version__
release   = ccman.__version__

source_suffix  = ".md"
source_parsers = { ".md": "recommonmark.parser.CommonMarkParser" } 

master_doc     = "index"