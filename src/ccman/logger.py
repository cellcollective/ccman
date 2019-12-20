# imports - standard imports
import os.path as osp
import logging

# imports - module imports
from   ccman._dict import Dict
import ccman

_FORMAT = "%(asctime)s %(levelname)s | %(message)s"
_LOGGER = None

def log(level = logging.ERROR, refresh = False):
    global _LOGGER

    logging.basicConfig()
    
    if not _LOGGER or refresh:
        logger = logging.getLogger(ccman.__name__)
        logger.setLevel(level)
        logger.propagate = False

        if not logger.handlers:
            formatter = logging.Formatter(_FORMAT, "%H:%M:%S")
            handler   = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # bench = getattr(ccman, "_bench", None)
        # if bench:
        #     path      = osp.join(bench.path, "logs", "bench.log") # pylint: disable=E1101

        #     handler   = logging.FileHandler(path)
        #     formatter = logging.Formatter(_FORMAT)
        #     handler.setFormatter(formatter)
        #     logger.addHandler(handler)

        # formats = Dict({ "bench": bench or "" })
        # logger  = logging.LoggerAdapter(logger, formats)

        _LOGGER = logger

    return _LOGGER