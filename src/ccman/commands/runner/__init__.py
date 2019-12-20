# imports - third-party imports
import click

# imports - module imports
from   ccman.commands.util import group_commands

@click.group("run")
def group():
    """
    Run Bench Processes
    """
    pass

command = group_commands(group, (
    "ccman.commands.runner.web",
    "ccman.commands.runner.db",
    "ccman.commands.runner.cache",
    "ccman.commands.runner._test",
    "ccman.commands.runner.app"
))