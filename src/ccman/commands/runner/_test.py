# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("test")
@click.pass_context
def command(ctx):
    """
    Run Cache Process
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.run("test")