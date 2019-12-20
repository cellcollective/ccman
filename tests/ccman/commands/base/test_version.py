import ccman

from   ccman.commands.base.version import VERSION_STRING, command

def test_version(runner, bench):
    result = runner.invoke(command, ["--bench", bench.path])
    output = VERSION_STRING.format(cc = bench.version,
        ccman = ccman.__version__)

    assert result.exit_code == 0
    assert result.output    == output