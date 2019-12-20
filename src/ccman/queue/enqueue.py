# imports - compatibility imports
import six

# imports - module imports
from   ccman.util.imports import import_handler
from   ccman.bench.util   import get_redis_connection
import ccman

def enqueue(method, *args, **kwargs):
    connection = get_redis_connection()
    queue      = rq.Queue(connection = connection)

    if isinstance(method, six.string_types):
        method = import_handler(method)
    
    queue.enqueue(method, *args, **kwargs)