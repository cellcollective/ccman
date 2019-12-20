# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("register")
@click.option("-r", "--remove",
    is_flag = True,
    help    = "Remove from Registry"
)
@click.pass_context
def command(ctx, remove = False):
    """
    Register a Bench
    """
    bench = ctx.obj["BENCH"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.register(remove = remove)