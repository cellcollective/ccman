# imports - standard imports
import os.path as osp

# imports - third-party imports
import pytest

# imports - module imports
from   ccman.commands.base.init import command
from   ccman.bench       import Site
from   ccman.util.crypto import generate_hash
import ccman

def test_init(runner, bench):
    def assert_initialized(result, bench, site):
        assert result.exit_code == 0
        assert osp.exists(osp.join(bench.path, "sites", site))

    site   = generate_hash()
    result = runner.invoke(command, [site, "--path", bench.path])
    assert_initialized(result, bench, site)

    assert bench.site == Site(site, bench)

    result = runner.invoke(command, [site, "--path", bench.path])
    assert result.exception

    result = runner.invoke(command, [site, "--path", bench.path, "--force"])
    assert not result.exception
    assert_initialized(result, bench, site)