# imports - compatibility imports
import six

# imports - standard imports
import os.path as osp
import getpass

# imports - module imports
import ccman
from   ccman.system import which, popen

class Playbook:
    def __init__(self, name):
        self.name = name

    @property
    def path(self):
        directory = ccman.path.playbooks
        path      = osp.join(directory, self.name)

        return path

    def run(self, variables = { }, tags = None, check = False, output = False, verbose = True):
        ansible   = which("ansible-playbook", raise_err = True)
        
        variables.update({ "user": getpass.getuser() })
        variables = " ".join(["%s=%s" % (k, v) for k, v in six.iteritems(variables)])
        
        command   = "%s %s %s %s %s %s" % (
            ansible,
            self.path,
            "--extra-vars '%s'" % variables if variables else "",
            "--tags %s"         % tags      if tags      else "",
            "--check" if check   else "",
            "-v"      if verbose else ""
        )

        if output:
            code, output, error = popen(command, output = True, raise_err = False)
            result = ccman.Dict({ 'code': code, 'output': output, 'error': error })

            return result
        else:
            popen(command)