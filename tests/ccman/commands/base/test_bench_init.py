# imports - standard imports
import os
import os.path as osp

# imports - third-party imports
import pytest

# imports - module imports
from   ccman.commands.base.init import command
import ccman

def test_init(runner):
    def assert_initialized(path, result):
        assert result.exit_code == 0
        assert "Bench Initialized at {path}".format(path = path) in result.output

    with runner.isolated_filesystem() as tmp:
        path   = osp.join(tmp, "test-bench")
            
        branch   = "master"
        protocol = "https"

        result   = runner.invoke(command, [
            "--name",   path,
            "--branch", branch
        ])
        assert_initialized(path, result)

        bench  = ccman.Bench(path)
        assert branch == str(bench.repo.active_branch)

        g      = bench.repo.git
        output = g.execute(["git", "remote", "show", "origin"])

        if protocol == "https":
            assert "https://" in output

        result = runner.invoke(command, [
            "--name", path
        ])
        assert result.exception

        result = runner.invoke(command, [
            "--name", path,
            "--force"
        ])
        assert_initialized(path, result)