# imports - compatibility imports
from __future__ import absolute_import

# imports - third-party imports
import click
import gitlab as glab

# imports - module imports
import ccman

def client(host = "https://git.unl.edu", token = None):
    if not token:
        token = ccman.get_config("gitlab_token",
            prompt = "ccman would like to know your GitLab Token ({host}/profile/account)".format(
                host = host
            )
        , crypt = True, global_ = True)
    else:
        ccman.cache.set_config("gitlab_token", token, crypt = True)
    
    ccman.log().info("GitLab Token found.")
    ccman.log().info("Using GitLab Host: {host}".format(host = host))
    gl = glab.Gitlab(host, private_token = token)

    try:
        ccman.log().info("Attempting to Authenticate to GitLab")
        gl.auth()
        ccman.log().info("Authentication Successful for user: {user}".format(user = gl.user.username))
    except Exception:
        raise ccman.AuthenticationError("Unable to authenticate to GitLab")

    return gl

def get_project(namespace, repository):
    gl      = client()

    ccman.log().info("Fetching Details for Project {namespace}/{repository}".format(
        namespace  = namespace,
        repository = repository
    ))
    project = gl.projects.get("{namespace}/{repository}".format(
        namespace  = namespace,
        repository = repository
    ))

    return project