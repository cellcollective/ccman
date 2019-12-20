# imports - standard imports
import os, os.path as osp

# imports - third-party imports
from jinja2 import Environment, FileSystemLoader

# imports - module imports
import ccman

def render_template(template, context = { }):
    """
    Render a template from the internal resources.
    """
    loader      = FileSystemLoader(ccman.path.templates)
    environment = Environment(loader = loader)

    template    = environment.get_template(template)
    ccman.log().info("Rendering Template %s with context: %s" % (template, context))
    string      = template.render(**context)

    return string