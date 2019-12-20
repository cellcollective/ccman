# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.environment import getenvvar

@click.command("web")
@click.option("-h", "--host",
    envvar  = getenvvar("WEB_HOST"),
    metavar = "HOST",
    help    = "Host Name"
)
@click.option("-p", "--port",
    type    = int,
    envvar  = getenvvar("WEB_PORT"),
    metavar = "PORT",
    help    = "Port Number"
)
@click.pass_context
def command(ctx, host = None, port = None):
    """
    Run Web Process
    """
    bench = ctx.obj["BENCH"]
    mode  = ctx.obj["ENVIRONMENT"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.run("web", host = host, port = port, mode = mode)