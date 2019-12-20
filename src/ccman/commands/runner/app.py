# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.environment import getenvvar

@click.command("app")
@click.option("-h", "--host",
    envvar  = getenvvar("APP_HOST"),
    metavar = "HOST",
    help    = "Host Name"
)
@click.option("-p", "--port",
    type    = int,
    envvar  = getenvvar("APP_PORT"),
    metavar = "PORT",
    help    = "Port Number"
)
@click.pass_context
def command(ctx, host = None, port = None):
    """
    Run App Process
    """
    bench = ctx.obj["BENCH"]
    mode  = ctx.obj["ENVIRONMENT"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.run("app", host = host, port = port, mode = mode)