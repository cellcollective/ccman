import os

import click

import ccman

@click.command("use")
@click.argument("site")
@click.pass_context
def command(ctx, site):
    """
    Use a Cell Collective Site as a default Site
    """
    bench      = ctx.obj["BENCH"]

    bench      = ccman.Bench(bench, search_parent_directories = True)
    bench.site = site