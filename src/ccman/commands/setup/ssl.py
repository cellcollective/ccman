# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("ssl")
@click.option("-s", "--site", "sites",
    default  = [ ],
    multiple = True,
    help     = "Site Name(s)"
)
@click.option("--silent",
    is_flag  = True,
    help     = "Silently Fail"
)
@click.pass_context
def command(ctx, sites = [ ]):
    """
    Setup SSL Certificates using Lets Encrypt
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.setup("ssl", sites = sites, raise_err = not silent)