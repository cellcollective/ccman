# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("workon")
@click.argument("branch")
@click.option("-r", "--remote",
    default = "upstream",
    help    = "Remote to checkout from"
)
@click.option("-t", "--track",
    default = "develop",
    help    = "Branch to checkout from"
)
@click.option("--tag",
    is_flag = True,
    help    = "Tag"
)
@click.option("--stash/--reset",
    default = True,
    help    = "Stash and Apply"
)
@click.option("--install/--no-install",
    default = True,
    help    = "Install after checkout"
)
@click.pass_context
def command(ctx, branch, remote = "upstream", track = "develop", tag = None, stash = True, install = True):
    """
    Work on a Branch
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.workon(branch = branch, remote = remote, track = track, tag = tag, stash = stash, install = install)