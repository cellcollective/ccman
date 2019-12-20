# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("request")
@click.argument("branch")
@click.option("-t", "--target",
    type     = click.Choice(["develop", "hotfix"]),
    default  = None,
    help     = "Target Branch"
)
@click.option("--title",
    default  = None,
    help     = "Merge Request Title"
)
@click.option("--label",
    multiple = True,
    help     = "Merge Request Label(s)"
)
@click.option("--description",
    default  = None,
    help     = "Merge Request Description"
)
@click.pass_context
def command(ctx, branch, target = None, title = None, description = None, label = [ ]):
    """
    Request for a merge
    """
    bench = ctx.obj["BENCH"]

    bench = ccman.Bench(bench, search_parent_directories = True)

    repo  = bench.repo
    repo.remotes.origin.fetch()

    if branch not in repo.remotes.origin.refs:
        raise ccman.ValueError("{branch} does not exists in remote - origin".format(
            branch = branch
        ))

    source = repo.remotes.origin.refs[branch]
    if not target:
        target = source.tracking_branch()
        if not target:
            while target not in ["develop", "hotfix"]:
                target = click.prompt("Target Branch (develop|hotfix)")

    if not title:
        title = click.prompt("Merge Request Title Description")
    
    gl      = ccman.gitlab.client()
    user    = gl.user

    project = ccman.gitlab.get_project(user.username, "cellcollective")
    base    = ccman.gitlab.get_project("helikarlab" , "cellcollective")
    
    project.mergerequests.create({
            "source_branch": branch,
            "target_branch": target,
        "target_project_id": base.id,
                    "title": title,
                   "labels": label
    })