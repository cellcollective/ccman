# imports - standard imports
import os
import logging

# imports - third-party imports
import click
import click_completion
from   click_didyoumean import DYMGroup

# imports - standard imports
from   ccman.commands.util import group_commands
from   ccman.environment   import getenvvar
import ccman

click_completion.init()

@click.group(
    name = ccman.__name__,
    cls  = DYMGroup,
    help = ccman.__description__,
    context_settings = dict(
        help_option_names = ["-h", "--help"]
    )
)
@click.version_option(
    version = ccman.get_version_str(),
    message = "%(version)s"
)
@click.option("-b", "--bench",
    type         = click.Path(file_okay = False),
    default      = os.getcwd(),
    show_default = True,
    envvar       = getenvvar("BENCH"),
    metavar      = "PATH",
    help         = "Cell Collective Bench"
)
@click.option("-s", "--site",
    default      = None,
    show_default = True,
    envvar       = getenvvar("SITE"),
    metavar      = "SITE",
    help         = "Bench Site"
)
@click.option("-e", "--environment",
    type         = click.Choice(["development", "production", "test"]),
    default      = "development",
    show_default = True,
    envvar       = getenvvar("ENVIRONMENT"),
    metavar      = "Type",
    help         = "Environment Type"
)
@click.option("-d", "--docker",
    is_flag      = True,
    envvar       = getenvvar("DOCKER"),
    help         = "Run command in a docker environment"
)
@click.option("-V", "--verbose",
    is_flag      = True,
    envvar       = getenvvar("VERBOSE"),
    metavar      = "VERBOSITY",
    help         = "Display Verbose Output"
)
@click.pass_context
def group(ctx, bench = os.getcwd(), site = None, environment = "development", docker = False, verbose = False):
    ctx.obj["BENCH"]       = bench
    ctx.obj["SITE"]        = site
    ctx.obj["ENVIRONMENT"] = environment
    ctx.obj["DOCKER"]      = docker
    ctx.obj["VERBOSE"]     = verbose

    if verbose:
        logger = logging.getLogger(ccman.__name__)
        logger.setLevel(logging.DEBUG)

command = group_commands(group, (
    "ccman.commands.base.init",
    "ccman.commands.base.version",
    "ccman.commands.base.help",
    "ccman.commands.base.config",
    "ccman.commands.base.register",

    "ccman.commands.site.init",
    "ccman.commands.site.use",
    "ccman.commands.site.restore",

    "ccman.commands.setup",
    
    "ccman.commands.develop.install",
    "ccman.commands.develop.build",
    "ccman.commands.develop.update",
    "ccman.commands.develop.clean",
    "ccman.commands.develop._test",

    "ccman.commands.develop.workon",
    "ccman.commands.develop.request",
    "ccman.commands.develop.release",
    
    "ccman.commands.develop.model",
    "ccman.commands.develop.migrate",
    "ccman.commands.develop.patch",
    "ccman.commands.develop.backup",
    "ccman.commands.develop.db",

    "ccman.commands.develop.deploy",

    "ccman.commands.develop.shell",
    "ccman.commands.develop.dbshell",

    "ccman.commands.develop.status",

    "ccman.commands.runner",
    "ccman.commands.runner.start",
    "ccman.commands.runner.stop"
))

def main():
    code = command(prog_name = ccman.__name__, obj = {}) # pylint: disable=E1111,E1123,E1120
    return code