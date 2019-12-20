# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.environment import getenvvar

@click.command("cache")
@click.option("-h", "--host",
    default = ccman.const.host.cache,
    envvar  = getenvvar("CACHE_HOST"),
    metavar = "HOST",
    help    = "Host Name"
)
@click.option("-p", "--port",
    type    = int,
    default = ccman.const.port.cache,
    envvar  = getenvvar("CACHE_PORT"),
    metavar = "PORT",
    help    = "Port Number"
)
@click.pass_context
def command(ctx, host = ccman.const.host.cache, port = ccman.const.port.cache):
    """
    Run Cache Process
    """
    bench = ctx.obj["BENCH"]
    mode  = ctx.obj["ENVIRONMENT"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.run("cache", host = host, port = port, mode = mode)