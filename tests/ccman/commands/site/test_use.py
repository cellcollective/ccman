# imports - standard imports
import os.path as osp

# imports - third-party imports
import pytest

# imports - module imports
from   ccman.commands.base.init import command
import ccman

def test_use(runner, bench, site):
    result = runner.invoke(command, [site.name, "--bench", bench.path])
    assert result.exit_code == 0

    assert bench.site == site.name