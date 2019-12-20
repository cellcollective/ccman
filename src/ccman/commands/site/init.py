# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
from   ccman.util.crypto import generate_hash
from   ccman.environment import getenvvar
import ccman

@click.command("site")
@click.argument("name")
@click.option("--db-name",
    help    = "DataBase Name"
)
@click.option("--db-username",
    default = generate_hash(),
    help    = "DataBase Username"
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
@click.option("--db-password",
    default = generate_hash(),
    help    = "DataBase Password"
)
@click.option("-f", "--force",
    is_flag = True,
    help    = "Force create site"
)
@click.pass_context
def command(ctx, name,
    db_name     = None,
    db_host     = None,
    db_port     = None,
    db_username = None,
    db_password = None,
    force       = False
):
    """
    Create new Cell Collective site
    """
    bench = ctx.obj["BENCH"]

    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.create_site(name,
        db_name     = db_name,
        db_host     = db_host,
        db_port     = db_port,
        db_username = db_username,
        db_password = db_password,
        force       = force
    )