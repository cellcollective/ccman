# imports - module imports
from ccman.util.types   import sequencify
from ccman.util.imports import import_handler
from ccman.util.string  import strip

# imports - third-party imports
import click

def group_commands(group, commands):
    """
    Add command-paths to a click.Group
    """
    commands = sequencify(commands, type_ = tuple)

    for command in commands:
        head, tail = command.rsplit(".", 1)
        tails      = ("", tail, "command")

        for i, tail in enumerate(tails):
            try:
                path    = "%s.%s" % (command, tail)
                command = import_handler(path)

                break
            except:
                if i == len(tails) - 1:
                    raise
        
        if isinstance(command, (click.core.Group, click.core.Command)):
            group.add_command(command)

    return group

def split_cmd_variables(str_var):
    _dict   = dict()

    str_var = str_var.split(" ")
    for var in str_var:
        key, value = [strip(string) for string in var.split("=")]
        _dict.update({ key: value })

    return _dict