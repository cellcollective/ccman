# imports - standard imports
import os

# imports - third-party imports
import click

# imports - module imports
import ccman

@click.command("test")
@click.option("--install/--no-install",
    default = False,
    help    = "Installation/Avoid Installation"
)
@click.option("--build/--no-build",
    default = False,
    help    = "Building/Avoid Building"
)
@click.option("-c", "--coverage",
    is_flag = True,
    help    = "Show Coverage Statistics"
)
@click.option("-f", "--fail",
    is_flag = True,
    help    = "Fail test on single"
)
@click.pass_context
def command(ctx, install = True, build = True, coverage = False, fail = False):
    """
    Test Runner
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    bench.test(
        install  = install,
        build    = build,
        coverage = coverage
    )