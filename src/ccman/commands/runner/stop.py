# imports - standard imports
import sys

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("stop")
@click.pass_context
def command(ctx):
    """
    Stop processes
    """
    bench = ctx.obj["BENCH"]
    mode  = ctx.obj["ENVIRONMENT"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    code  = bench.stop()

    sys.exit(code)