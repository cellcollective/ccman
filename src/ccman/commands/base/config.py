import os

import click

import ccman

@click.command("config")
@click.argument("key")
@click.argument("value")
@click.option("-g", "--global", "g",
    is_flag = True,
    help    = "Set Config Globally"
)
@click.option("-c", "--crypt",
    is_flag = True,
    help    = "Encrypt"
)
@click.pass_context
def command(ctx, key, value, g = False, crypt = False):
    """
    Set Config
    """
    bench = ctx.obj["BENCH"]
    site  = ctx.obj["SITE"]

    if not g:
        bench = ccman.Bench(bench, search_parent_directories = True)
        if site:
            # TODO: Get site and set config
            pass
        else:
            bench.set_config(key, value, crypt = crypt)
    else:
        ccman.cache.set_config(key, value, crypt = crypt)