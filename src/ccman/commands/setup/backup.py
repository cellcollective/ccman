# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("backup")
@click.pass_context
def command(ctx):
    """
    Setup Backup
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)