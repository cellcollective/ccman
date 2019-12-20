# imports - standard imports
import os
import os.path as osp

# imports - third-party imports
import git
import click

# imports - module imports
import ccman

VERSION_STRING = \
"""
Cell Collective         v{cc}-{branch} ({commit})
Cell Collective Manager v{ccman}-{ccman_branch} ({ccman_commit})
"""

@click.command("version")
@click.pass_context
def command(ctx):
    """
    Display Cell Collective and Manager Version
    """

    bench      = ctx.obj["BENCH"]

    bench      = ccman.Bench(bench, search_parent_directories = True)
    
    ccman_path = osp.join(bench.path, ".ccman")
    ccman_repo = git.Repo(ccman_path)

    version    = VERSION_STRING.format(cc = bench.version,
        branch = bench.repo.active_branch,
        commit = bench.repo.git.rev_parse(bench.repo.head.commit, short = 7),
        ccman  = ccman.__version__,
        ccman_branch = ccman_repo.active_branch,
        ccman_commit = ccman_repo.git.rev_parse(ccman_repo.head.commit, short = 7)
    )

    click.echo(version, nl = False)