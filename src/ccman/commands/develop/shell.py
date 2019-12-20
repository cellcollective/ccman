# imports - compatibility imports
from   six import iteritems

# imports - standard imports
import sys
import os
import os.path as osp

# imports - third-party imports
import click
import IPython

# imports - module imports
import ccman
from   ccman.system import popen, which, makedirs

@click.command("shell")
@click.option("-i", "--interpreter",
    type    = click.Choice(["node", "babel-node"]),
    default = "babel-node",
    help    = "Interpreter to be used.",
)
@click.pass_context
def command(ctx, interpreter = "babel-node"):
    """
    Launch the console
    """
    bench = ctx.obj["BENCH"]
    bench = ccman.Bench(bench, search_parent_directories = True)

    bench.init()

    path  = bench.repo.working_dir
    popen("npx %s" % interpreter, cwd = path)