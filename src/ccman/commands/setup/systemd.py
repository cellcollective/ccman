# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("systemd")
@click.option("--build/--no-build",
    help    = "Build Configurations"
)
@click.pass_context
def command(ctx, build = True):
    """
    Setup sysetmd configuration
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    bench._build_systemd_config(force = build)