# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("patch")
@click.option("--no-check",
    is_flag = True,
    help    = "Avoid checking if bench is valid."
)
@click.pass_context
def command(ctx, no_check = False):
    """
    Run Patches
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = not no_check)
    bench.patch()