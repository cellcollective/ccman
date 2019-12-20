# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("nginx")
@click.option("--build/--no-build",
    help    = "Build Configurations"
)
@click.pass_context
def command(ctx, build = True):
    """
    Setup nginx configuration
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    bench._build_nginx_configs(force = build)