# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("clean")
@click.option("-f", "--force",
    is_flag = True,
    help    = "Force Clean Strategy"
)
@click.option("-d", "--destroy",
    is_flag = True,
    help    = "Destroy Clean Strategy"
)
@click.pass_context
def command(ctx, force = False, destroy = False):
    """
    Clean the Bench
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.clean(force = force, destroy = destroy)