# imports - standard imports
import os, os.path as osp

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.commands.util import split_cmd_variables
from   ccman.util import json as _json

@click.command("build")
@click.option("--watch",
    is_flag = True,
    help    = "Watch for change in Cell Collective App"
)
@click.option("-v", "--vars", "variables",
    help    = "Extra Variables"
)
@click.option("--ignore",
    type     = click.Choice(["app"]),
    multiple = True,
    help     = "Ignore app build"
)
@click.option("--install",
    is_flag  = True,
    help     = "Install"
)
@click.option("--locales",
    is_flag  = True,
    help     = "Build Languages"
)
@click.pass_context
def command(ctx, install = False, watch = False, variables = None, ignore = [ ], locales = False):
    """
    Build the Cell Collective App
    """
    bench = ctx.obj["BENCH"]
    mode  = ctx.obj["ENVIRONMENT"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.build(
        mode      = mode,
        install   = install, 
        watch     = watch,
        variables = variables,
        ignore    = ignore,
        locales   = locales
    )