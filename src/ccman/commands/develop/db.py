# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.system      import which, popen
from   ccman.environment import getenvvar

@click.command("db",
    context_settings = dict(
        help_option_names = ["-h", "--help"]
    )
)
@click.argument("args", nargs = -1)
@click.pass_context
def command(ctx,
    args = [ ]
):
    """
    Run DataBase Migrations
    """
    bench     = ctx.obj["BENCH"]

    bench     = ccman.Bench(bench, search_parent_directories = True)

    if not args:
        args  = ["--help"]
    
    popen("yarn db %s" % " ".join(args),
        cwd = bench.repo.working_dir)