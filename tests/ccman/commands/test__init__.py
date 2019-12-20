# imports - standard imports
import os.path as osp

# imports - module imports
import ccman
from   ccman.commands import command

def test_command(runner):
    result = runner.invoke(command, ["--version"])
    
    assert result.exit_code == 0
    assert result.output    == "{version}\n".format(
        version = ccman.__version__
    )
