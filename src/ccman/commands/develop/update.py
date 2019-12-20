# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.commands.util import split_cmd_variables

@click.command("update")
@click.option("-r", "--remote",
    default = "upstream",
    help    = "Remote name to update from"
)
@click.option("-b", "--branch",
    default = "develop",
    help    = "Branch name to update from"
)
@click.option("--reset/--no-reset",
    is_flag = True,
    default = True,
    help    = "Reset during checkout"
)
@click.option("--ccman-only",
    is_flag = True,
    help    = "Only Update ccman"
)
@click.option("-v", "--vars", "variables",
    help    = "Extra Variables"
)
@click.pass_context
def command(ctx,
    remote       = "upstream",
    branch       = "develop",
    reset        = True,
    ccman_only   = False,
    variables    = None
):
    """
    Update Cell Collective
    """
    bench = ctx.obj["BENCH"] 
    mode  = ctx.obj["ENVIRONMENT"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.update(ccman_only = ccman_only, mode = mode, remote = remote, branch = branch, clean = not ccman_only, patch = not ccman_only,
        build = not ccman_only, reset = reset, variables = variables)