# imports - standard imports
import os
import getpass

# imports - third-party imports
import click

# imports - module imports
from   ccman.ansible import Playbook
import ccman

@click.command("install")
@click.pass_context
def command(ctx):
    """
    Install Cell Collective Dependencies
    """
    bench = ctx.obj["BENCH"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.install()