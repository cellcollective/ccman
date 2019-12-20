# imports - standard imports
import os
import time

# imports - third-party imports
import click

try:
    from slack import WebClient
    SLACK_CLIENT_MAJOR_VERSION = 2
except ImportError:
    from slackclient import SlackClient as WebClient
    SLACK_CLIENT_MAJOR_VERSION = 1

# imports - module imports
from   ccman.ansible    import Playbook
from   ccman.util.types import dict_filter
import ccman

def _slack_client_post_message(client, channel, text):
    if SLACK_CLIENT_MAJOR_VERSION == 2:
        client.chat_postMessage(
            channel = channel,
            text    = text
        )
    else:
        client.api_call('chat.postMessage', 
            channel = channel,
            text    = text
        )

@click.command("deploy")
@click.option("-h", "--host",
    required = True,
    help     = "Host Name"
)
@click.option("-u", "--user",
    default  = "helikarlab",
    help     = "Remote User"
)
@click.option("--branch",
    default  = "develop",
    help     = "Branch Name to update from"
)
@click.option("-c", "--config",
    help     = "Extra Variables"
)
@click.option("--check/--no-check",
    default  = False,
    help     = "Check Before Execution",
)
@click.option("--notify/--silent",
    default  = True,
    help     = "Notify to Hook"
)
@click.option("--wait",
    type     = int,
    default  = 60 * 3,
    help     = "Wait time (in seconds) period before deploy"
)
@click.option("--verbose",
    is_flag  = True,
    help     = "Increase verbosity"
)
@click.pass_context
def command(ctx, host, user = "helikarlab", bench = "~/ccbench", branch = "develop",
    config = None, check = False, notify = True, wait = 60 * 3, verbose = False):
    """
    Deploy Cell Collective to Server
    """
    bench = ctx.obj["BENCH"]
    mode  = ctx.obj["ENVIRONMENT"]
    
    if notify:
        project = ccman.gitlab.get_project("helikarlab", "cellcollective")
        commit  = project.commits.list()[0].short_id
        version = project.tags.list()[0].name

        build   = "{version}-{branch} ({commit})".format(
            version = version,
            branch  = branch,
            commit  = commit
        )

        token   = ccman.get_config("slack_api_token")
        if not token:
            token  = click.prompt("Slack API Token")
            ccman.cache.set_config("slack_api_token", token)
        
        client  = WebClient(token)
        channel = "CAQFSMGAJ"
        text    = \
"""
Deploying {build} to {host} in {time} minutes.
Configuration Details:
```
mode   = {mode}
branch = {branch}
config = {config}
```
WARNING: Kindly save all ongoing work to avoid loss.
""".format(build = build, host = host, time = wait / 60,
    mode   = mode,
    branch = branch,
    config = config
)

        slack_client_post_message(client, channel = channel, text = text)

    ccman.log().info("Sleeping for {time} seconds".format(time = wait))
    time.sleep(wait)

    context  = dict(
        hosts     = host,
        user      = user,
        bench     = bench,
        branch    = branch,
        config    = config,
        mode      = mode
    )
    context  = dict_filter(context, None)
    
    playbook = Playbook("deploy.yml")
    
    try:
        if notify:
            slack_client_post_message(client, channel = channel, text = "Deploy Progress.")
        playbook.run(variables = context, check = check, verbose = verbose)
    except Exception:
        if notify:
            slack_client_post_message(client, channel = channel, text = "Deploy Failure.")
        raise

    if notify:
        slack_client_post_message(client, channel = channel, text = "Deploy Success.")