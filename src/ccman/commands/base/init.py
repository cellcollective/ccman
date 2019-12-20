# imports - standard imports
import sys

# imports - third-party imports
import click

# imports - module imports
from   ccman.environment import getenvvar
import ccman

@click.command("init")
@click.argument("name",
    required  = False,
    default   = "ccbench"
)
@click.option("--python",
    default = sys.executable,
    help    = "Path to Python Executable"
)
@click.option("-p", "--protocol",
    type    = click.Choice(["https", "ssh"]),
    default = "https",
    help    = "Protocol for git to be used"
)
@click.option("-b", "--branch",
    default = "develop",
    help    = "Branch to checkout from"
)
@click.option("--web-host",
    default = ccman.const.host.web,
    envvar  = getenvvar("WEB_HOST"),
    metavar = "HOST",
    help    = "Web Host"
)
@click.option("--web-port",
    type    = int,
    default = ccman.const.port.web,
    envvar  = getenvvar("WEB_PORT"),
    metavar = "PORT",
    help    = "Web Port"
)
@click.option("--app-host",
    default = ccman.const.host.app,
    envvar  = getenvvar("APP_HOST"),
    metavar = "HOST",
    help    = "App Host"
)
@click.option("--app-port",
    type    = int,
    default = ccman.const.port.app,
    envvar  = getenvvar("APP_PORT"),
    metavar = "PORT",
    help    = "App Port"
)
@click.option("--db-host",
    default = ccman.const.host.db,
    envvar  = getenvvar("DB_HOST"),
    metavar = "HOST",
    help    = "DataBase Host"
)
@click.option("--db-port",
    type    = int,
    default = ccman.const.port.db,
    envvar  = getenvvar("DB_PORT"),
    metavar = "PORT",
    help    = "DataBase Port"
)
@click.option("--cache-host",
    default = ccman.const.host.cache,
    envvar  = getenvvar("CACHE_HOST"),
    metavar = "HOST",
    help    = "Cache Host"
)
@click.option("--cache-port",
    type    = int,
    default = ccman.const.port.cache,
    envvar  = getenvvar("CACHE_PORT"),
    metavar = "PORT",
    help    = "Cache Port"
)
@click.option("-s", "--site",
    default = "site.local",
    help    = "Site Name"
)
@click.option("--no-site",
    is_flag = True,
    help    = "Avoid Creating a site"
)
@click.option("-f", "--force",
    is_flag = True,
    help    = "Force Create a Cell Collective Bench"
)
@click.pass_context
def command(ctx,
    name         = "ccbench",
    protocol     = "https",
    branch       = "develop",
    python       = sys.executable,
    web_host     = ccman.const.host.web,
    web_port     = ccman.const.port.web,
    app_host     = ccman.const.app.host,
    app_port     = ccman.const.app.port,
    db_host      = ccman.const.host.db,
    db_port      = ccman.const.port.db,
    cache_host   = ccman.const.host.cache,
    cache_port   = ccman.const.port.cache,
    site         = "site.local",
    no_site      = False,
    force        = False
):
    """
    Initialize a Cell Collective Bench
    """
    mode   = ctx.obj["ENVIRONMENT"]
    docker = ctx.obj["DOCKER"] 

    bench = ccman.Bench(name)
    bench.create(
        protocol     = protocol,
        branch       = branch,
        python       = python,
        web_host     = web_host,
        web_port     = web_port,
        app_host     = app_host,
        app_port     = app_port,
        db_host      = db_host,
        db_port      = db_port,
        cache_host   = cache_host,
        cache_port   = cache_port,
        site         = None if no_site or docker else site,
        force        = force,
        mode         = mode
    )

    click.echo("Bench Initialized at {path}".format(path = bench.path))