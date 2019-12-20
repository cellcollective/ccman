# imports - standard imports
import os
import os.path as osp

# imports - third-party imports
import click

# imports - module imports
from ccman.system import popen
import ccman

@click.command("model")
@click.option("--build/--no-build",
    is_flag = True,
    default = True,
    help    = "Build Config"
)
@click.option("-c", "--create",
    help    = "Create a Migration File"
)
@click.option("-a", "--args",
    help    = "Arguments"
)
@click.pass_context
def command(ctx, build = True, create = None, args = None):
    """
    Migrate Bench Sites
    """
    bench = ctx.obj["BENCH"]
    
    bench = ccman.Bench(bench, search_parent_directories = True)
    if build:
        bench._build_sequelize_config()

    cc    = osp.join(bench.repo.working_dir, "cc")

    if create:
        command  = "model:generate --name {name} {args}".format(
            name = create,
            args = args
        )

    popen("npx sequelize               \
        --config          {config}     \
        --models-path     {models}     \
        --migrations-path {migrations} \
        --seeders-path    {seeders}    \
        {command}".format(
        config     = osp.join(bench.path, "configs", "sequelize", "config.json"),
        models     = osp.join(cc, "models"),
        migrations = osp.join(cc, "migrations"),
        seeders    = osp.join(cc, "seeders"),
        command    = command
    ), cwd = cc)