# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman
from   ccman.system      import which, popen
from   ccman.environment import getenvvar

@click.command("dbshell")
@click.option("-i", "--interface",
    type    = click.Choice(["pgcli", "psql"]),
    default = "pgcli",
    help    = "Interface to use"
)
@click.option("--interactive",
    is_flag = True,
    help    = "Run in Interactive Mode"
)
@click.option("-d", "--database",
    help    = "DataBase Name"
)
@click.option("-h", "--host",
    envvar  = getenvvar("DB_HOST"),
    metavar = "HOST",
    help    = "Host Name"
)
@click.option("-P", "--port",
    type    = int,
    envvar  = getenvvar("DB_PORT"),
    metavar = "PORT",
    help    = "Port Number"
)
@click.option("-U", "--username",
    envvar  = getenvvar("DB_USERNAME"),
    metavar = "USERNAME",
    help    = "Username"
)
@click.option("--password",
    envvar  = getenvvar("DB_PASSWORD"),
    metavar = "PASSWORD",
    help    = "Password"
)
@click.pass_context
def command(ctx,
    site        = None,
    interface   = "pgcli",
    interactive = None,
    database    = None,
    host        = None,
    port        = None,
    username    = None,
    password    = None
):
    """
    Launch the Database Interface Shell
    """
    interface = which(interface, raise_err = True)
    bench     = ctx.obj["BENCH"]
    site      = ctx.obj["SITE"]

    bench     = ccman.Bench(bench, search_parent_directories = True)

    name      = site or bench.site.name
    site      = ccman.Site(name, bench)

    database  = database or site.cache.get_config("database_name")
    if not database:
        raise ccman.ValueError("DataBase name not found.")
        
    host      = host     or bench.get_config("database_host")
    port      = port     or bench.get_config("database_port")
    username  = username or site.cache.get_config("database_username")
    password  = password or site.cache.get_config("database_password")

    command   = " ".join([
        interface,
        "-h {host}".format(host = host)     if host     else "",
        "-p {port}".format(port = port)     if port     else "",
        "-U {user}".format(user = username) if username else "",
        "-w",
        "-d", database,
        "--less-chatty"                                if "pgcli" in interface else "",
        "--prompt '{site}> '".format(site = site.name) if "pgcli" in interface else ""
    ])

    popen(command, env = dict(
        PGPASSWORD = password if password else ""
    ))