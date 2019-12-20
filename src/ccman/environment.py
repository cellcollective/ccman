# imports - standard imports
import os

# imports - module imports
from   ccman.util.types import auto_typecast
import ccman

PREFIX = "CC"

def getenvvar(name, prefix = PREFIX, seperator = "_"):
	if not prefix:
		seperator = ""

	envvar = "%s%s%s" % (prefix, seperator, name)
	return envvar

def getenv(name, default = None, cast = True, prefix = PREFIX, seperator = "_", raise_err = False):
    envvar = getenvvar(name, prefix = prefix, seperator = seperator)

    if not envvar in list(os.environ) and raise_err:
        raise ccman.KeyError("Environment Variable %s not found." % envvar)

    value  = os.getenv(envvar, default)
    value  = auto_typecast(value) if cast else value

    return value

def setenv(name, value, prefix = PREFIX, seperator = "_", force = False):
	envvar = getenvvar(name, prefix = prefix, seperator = "_")
	value  = value_to_envval(value)

	if envvar not in os.environ or force:
		os.environ[envvar] = value

def value_to_envval(value):
	"""
	Convert python types to environment values
	"""
	if not isinstance(value, str):
		if isinstance(value, int):
			value = str(value)
		elif value is True:
			value = "true"
		elif value is False:
			value = "false"
		else:
			raise TypeError("Unknown parameter type %s with value %r" % (value, type(value)))

	return value