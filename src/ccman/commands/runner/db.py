# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.environment import getenvvar

@click.command("db")
@click.option("-h", "--host",
    default = ccman.const.host.db,
    envvar  = getenvvar("DB_HOST"),
    metavar = "HOST",
    help    = "Host Name"
)
@click.option("-p", "--port",
    default = ccman.const.port.db,
    type    = int,
    envvar  = getenvvar("DB_HOST"),
    metavar = "PORT",
    help    = "Port Number"
)
@click.pass_context
def command(ctx, host = ccman.const.host.db, port = ccman.const.port.db):
    """
    Run DataBase Process
    """
    bench = ctx.obj["BENCH"]
    mode  = ctx.obj["ENVIRONMENT"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.run("db", host = host, port = port, mode = mode)