# imports - standard imports
import os.path as osp

# imports - module imports
import ccman
from   ccman.logger import log
from   ccman.system import read

# def test_log(bench):
#     ccman._bench = bench
#     logger       = log()
#     logger.info("foobar")

#     path = osp.join(bench.path, "logs", "bench.log")
#     assert osp.exists(path)

#     logs = read(path)
#     assert str(bench) in logs
#     assert "foobar"   in logs