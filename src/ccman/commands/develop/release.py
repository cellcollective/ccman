# imports - standard imports
import os

# imports - third-party imports
import click
import semver
import git

# imports - module imports
import ccman

def update_branch(repo, branch, remote = None):
    track = "{remote}/{branch}".format(
        remote = remote,
        branch = branch
    )
    
    g     = repo.git
    g.fetch("--all" if not remote else remote)
    g.checkout(B = branch, t = track)
    g.reset("--hard", track)

def get_release_log(repo, remote, source, target):
    g     = repo.git

    log   = g.log("{remote}/{target}..{remote}/{source}".format(
        remote = remote,
        source = source,
        target = target
    ), "--format=format:%s", "--no-merges")

    log   = log.splitlines()
    log   = "\n".join(["{i}. {line}".format(i = i + 1, line = line)
        for i, line in enumerate(log)
    ])

    return log

def get_next_version(previous, type_):
    version = previous

    if   type_ == "major":
        version = semver.bump_major(previous)
    elif type_ == "minor":
        version = semver.bump_minor(previous)
    elif type_ == "patch":
        version = semver.bump_patch(previous)
    
    return version

def prompt_merge_conflict(exception, source, target):
    click.echo("""
ERROR: Merge Conflict while merging {source} into {target}.
Manually resolve the Merge Conflicts and try again.
""".format(
        source = source,
        target = target
    ))

    value = click.confirm("Did you resolve merge conflicts?")

    return value

@click.command("release")
@click.argument("type",
    type    = click.Choice(["major", "minor", "patch"])
)
@click.option("-s", "--source",
    type    = click.Choice(["develop", "hotfix"]),
    default = "develop",
    help    = "From Branch"
)
@click.option("-t", "--target",
    default = "master",
    help    = "To Branch"
)
@click.pass_context
def command(ctx, type, source = "develop", target = "master"):
    """
    Release a new version
    """
    bench  = ctx.obj["BENCH"]
    
    bench  = ccman.Bench(bench, search_parent_directories = True)
    repo   = bench.repo

    remote = "upstream"
    target = target

    update_branch(repo = repo, branch = source, remote = remote)
    update_branch(repo = repo, branch = target, remote = remote)

    HOTFIX = source == "hotfix"

    if HOTFIX:
        update_branch(repo = repo, branch = "develop", remote = remote)
    else:
        update_branch(repo = repo, branch = "hotfix",  remote = remote)

    g      = repo.git
    g.checkout(source)
    
    log    = get_release_log(repo, remote, source, target)
    
    if not log:
        click.echo("No commits found to release.")
    else:
        prev_version = bench.version
        next_version = get_next_version(prev_version, type)

        click.echo("Releasing Version: {version}".format(version = next_version))
        click.echo("Description: \n{description}".format(description = log))

        if click.confirm("Do you wish to continue?"):
            bench.version = next_version
            
            g.checkout(target)
            try:
                g.merge(source, "--no-ff")
            except git.exc.GitCommandError as e:
                while not prompt_merge_conflict(e, source = source, target = target):
                    pass
            
            tag = "v{version}".format(version = next_version)
            repo.create_tag(tag, message = "Release {version}".format(
                version = next_version
            ))
            
            # Keep Branches even.
            g.checkout(source)
            try:
                g.merge(target)
            except git.exc.GitCommandError as e:
                while not prompt_merge_conflict(e, source = source, target = target):
                    pass

            if HOTFIX:
                g.checkout("develop")
                try:
                    g.merge(target)
                except git.exc.GitCommandError as e:
                    while not prompt_merge_conflict(e, source = source, target = target):
                        pass
            else:
                g.checkout("hotfix")
                try:
                    g.merge(target)
                except git.exc.GitCommandError as e:
                    while not prompt_merge_conflict(e, source = source, target = target):
                        pass

            # Pushing Release.
            args = [
                "{source}:{source}".format(source = source),
                "{target}:{target}".format(target = target),
                tag
            ]

            if HOTFIX:
                args.append("develop:develop")
            else:
                args.append("hotfix:hotfix")

            g.push(remote, *args)

            # Create GitLab Release.
            project = ccman.gitlab.get_project("helikarlab", "cellcollective")
            tag     = project.tags.get(tag)

            tag.set_release_description(log)