# imports - standard imports
import os.path as osp

# imports - third-party imports
import pytest
from   click.testing import CliRunner

# imports - module imports
import ccman
from   ccman.bench import Site

@pytest.fixture()
def runner():
    runner = CliRunner()
    return runner

@pytest.fixture()
def bench(tmpdir):
    tmp   = tmpdir.mkdir("tmp")
    path  = osp.join(str(tmp), "ccbench")

    bench = ccman.Bench(path)
    bench.create()
    
    return bench

@pytest.fixture()
def site(bench):
    name = "foo.bar"

    bench.create_site(name)
    site = Site(name, bench)
    
    return site