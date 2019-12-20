# imports - standard imports
import os
import json

# imports - third-party imports
import click

# imports - module imports
import ccman

_status_service_help = "Ignore %s status"

@click.command("status")
@click.option("--web/--no-web",
    is_flag  = True,
    default  = True,
    help     = _status_service_help % "web"
)
@click.option("--app/--no-app",
    is_flag  = True,
    default  = True,
    help     = _status_service_help % "app"
)
@click.option("--db/--no-db",
    is_flag  = True,
    default  = True,
    help     = _status_service_help % "db"
)
@click.option("--cache/--no-cache",
    is_flag  = True,
    default  = True,
    help     = _status_service_help % "cache"
)
@click.option("--ok",
    is_flag  = True,
    help     = "Returns status in boolean mode."
)
@click.option("-v", "--verbose",
    is_flag  = True,
    help     = "Display Verbose Output"
)
@click.pass_context
def command(ctx, web = True, app = True, db = True, cache = True, verbose = False, ok = False):
    """
    Check Bench Status
    """
    bench  = ctx.obj["BENCH"]
    
    bench  = ccman.Bench(bench, search_parent_directories = True)
    report = bench.status(web = web, app = app, db = db, cache = cache, verbose = verbose)

    status = True

    if ok:
        if verbose:
            status = all([service.status for service in report.values()])
        else:
            status = all(report.values())
    else:
        status = json.dumps(report, indent = 4)

    if ok:
        if not status:
            raise ccman.CCError("Services not running: %s" % report)
        else:
            status = "true"
    
    click.echo(status)