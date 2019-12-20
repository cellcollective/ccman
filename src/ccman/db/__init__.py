# imports - standard imports
import os.path as osp

# imports - third-party imports
import dataset

# imports - module imports
from   ccman.system      import read
from   ccman.util.string import strip
import ccman

def _get_queries(buffer):
    queries = [ ]
    lines   = buffer.split(";")
    
    for line in lines:
        line = strip(line)
        queries.append(line)

    return queries

def connect(connection, bootstrap = True):
    db      = dataset.connect(connection)

    path    = osp.join(ccman.path.data, "bootstrap.sql")
    buffer  = read(path)

    queries = _get_queries(buffer)
    
    for query in queries:
        db.query(query)

    return db 