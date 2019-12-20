# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("restore")
@click.argument("dbfile")
@click.argument("static",
    required = False
)
@click.option("--silent/--no-silent",
    is_flag  = True,
    help     = "Fail/Don't Fail Silently"
)
@click.option("-f", "--force",
    is_flag  = True,
    help     = "Force Restore"
)
@click.pass_context
def command(ctx, dbfile, static = None, silent = True, force = False):
    """
    Restore Sites
    """
    bench = ctx.obj["BENCH"]
    site  = ctx.obj["SITE"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.restore(site, dbfile, static = static, raise_err = not silent, force = force)