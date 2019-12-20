# imports - standard imports
import os, os.path as osp
import sys

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.environment import getenvvar

SERVICES = ("web", "app", "cache", "db", "docs")

@click.command("start")
# @click.option("--web-host",
#     envvar  = getenvvar("WEB_HOST"),
#     metavar = "HOST",
#     help    = "Web Host Name"
# )
# @click.option("--web-port",
#     type    = int,
#     envvar  = getenvvar("WEB_PORT"),
#     metavar = "PORT",
#     help    = "Web Port Number"
# )
# @click.option("--app-host",
#     envvar  = getenvvar("APP_HOST"),
#     metavar = "HOST",
#     help    = "App Host Name"
# )
# @click.option("--app-port",
#     type    = int,
#     envvar  = getenvvar("APP_PORT"),
#     metavar = "PORT",
#     help    = "App Port Number"
# )
# @click.option("--db-host",
#     envvar  = getenvvar("DB_HOST"),
#     metavar = "HOST",
#     help    = "DataBase Host Name"
# )
# @click.option("--db-port",
#     type    = int,
#     envvar  = getenvvar("DB_PORT"),
#     metavar = "PORT",
#     help    = "DataBase Port Number"
# )
# @click.option("--cache-host",
#     envvar  = getenvvar("CACHE_HOST"),
#     metavar = "HOST",
#     help    = "Cache Host Name"
# )
# @click.option("--cache-port",
#     type    = int,
#     envvar  = getenvvar("CACHE_PORT"),
#     metavar = "PORT",
#     help    = "Cache Port Number"
# )
@click.option("--install",
    is_flag = True,
    help    = "Installation"
)
@click.option("--build",
    is_flag = True,
    help    = "Building"
)
@click.option("-v", "--vars", "variables",
    help    = "Extra Build Variables"
)
@click.option("--ignore",
    type     = click.Choice(SERVICES),
    multiple = True,
    help     = "Processes to Ignore"
)
@click.option("--quiet",
    type     = click.Choice(SERVICES),
    multiple = True,
    help     = "Processes to Quieten"
)
@click.pass_context
def command(ctx,
    install    = False,
    build      = False,
    docs       = True,
    variables  = None,
    ignore     = [ ],
    quiet      = [ ]
):
    """
    Start the Development Processes
    """
    bench = ctx.obj["BENCH"]
    mode  = ctx.obj["ENVIRONMENT"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    code  = bench.start(
        mode       = mode,
        install    = install,
        build      = True if variables else build,
        variables  = variables,
        ignore     = ignore,
        quiet      = quiet
    )

    sys.exit(code)