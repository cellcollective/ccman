# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("backup")
@click.option("--compress/--no-compress",
    default  = True,
    help     = "Compress after backup"
)
@click.option("--silent/--no-silent",
    help     = "Fail/Don't Fail Silently"
)
@click.pass_context
def command(ctx, compress = True, silent = True):
    """
    Backup Sites
    """
    bench = ctx.obj["BENCH"]
    site  = ctx.obj["SITE"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.backup(sites = site, compress = compress, raise_err = not silent)