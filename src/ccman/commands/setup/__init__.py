# imports - third-party imports
import click

# imports - standard imports
import ccman
from   ccman.commands.util import group_commands

@click.group("setup")
def group():
    """
    Setup Commands
    """
    pass

command = group_commands(group, (
    "ccman.commands.setup.nginx",
    "ccman.commands.setup.systemd",
    "ccman.commands.setup.backup"
))