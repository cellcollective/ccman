# imports - compatibility imports
import six

# imports - standard imports
import os
import os.path as osp
import errno
import subprocess
from   distutils.spawn import find_executable
import shutil
import collections
import socket
import io

# imports - module imports
from   ccman.util.string import strip
import ccman

def read(fname, encoding = "utf8"):
    with io.open(fname, encoding = encoding) as f:
        data = f.read()
    return data

def write(fname, data = None, force = False):
    fname = str(fname)
    
    if not osp.exists(fname) or force:
        ccman.log().info("Writing File {fname} with data {data}".format(
            fname = fname,
            data  = data
        ))

        with open(fname, "w") as f:
            if data:
                f.write(data)

def link(source, target, exist_ok = False):
    source = osp.realpath(str(source))
    target = osp.realpath(str(target))

    if osp.exists(target) or osp.islink(target):
        if not exist_ok:
            raise OSError("{path} already exists.".format(
                path = target
            ))
    else:
        ccman.log().info("Symlinking source {source} with target {target}".format(
            source = source,
            target = target
        ))
        os.symlink(source, target)

def which(exec_, raise_err = False):
    executable = find_executable(exec_)
    if not executable and raise_err:
        raise ccman.ValueError("{executable} executable not found.".format(
            executable = exec_
        ))
    
    return executable

def popen(*args, **kwargs):
    wait        = kwargs.get("wait", True)
    output      = kwargs.get("output", False)
    directory   = kwargs.get("cwd")
    environment = kwargs.get("env")
    shell       = kwargs.get("shell", True)
    raise_err   = kwargs.get("raise_err", True)

    environ     = os.environ.copy()
    if environment:
        environ.update(environment)

    for k, v in six.iteritems(environ):
        environ[k] = str(v)

    command     = " ".join([str(arg) for arg in args])
    ccman.log().info("Running command: {command} with environment variables: {variables}".format(
        command   = command,
        variables = environment
    ))
    
    proc        = subprocess.Popen(command,
        stdin   = subprocess.PIPE if output else None,
        stdout  = subprocess.PIPE if output else None,
        stderr  = subprocess.PIPE if output else None,
        env     = environ,
        cwd     = directory,
        shell   = shell
    )

    if wait:
        code = proc.wait()

        if code and raise_err:
            raise ccman.PopenError(code, command)
        
        if output:
            output, error = proc.communicate()

            if output:
                output = output.decode("utf-8")
                output = strip(output)

            if error:
                error  = error.decode("utf-8")
                error  = strip(error)

            ccman.log().info("Status Code: {code}".format(code = code))

            ccman.log().info("Output Recieved")
            ccman.log().info(output)

            ccman.log().warning("Error Recieved")
            ccman.log().warning(error)

            return code, output, error
        else:
            ccman.log().info("Status Code: {code}".format(code = code))
            
            return code

    return proc

def pardir(fname, level = 1):
    fname = str(fname)

    for _ in range(level):
        fname = osp.dirname(fname)
    return fname

def makedirs(dirs, exist_ok = False):
    dirs = str(dirs)
    
    try:
        os.makedirs(dirs)
    except OSError as e:
        if not exist_ok or e.errno != errno.EEXIST:
            raise

def remove(path, recursive = False, raise_err = True):
    path = str(path)
    path = osp.realpath(path)

    if osp.isdir(path):
        if recursive:
            shutil.rmtree(path)
        else:
            if raise_err:
                raise OSError("{path} is a directory.".format(
                    path = path
                ))
    else:
        try:
            os.remove(path)
        except OSError:
            if raise_err:
                raise

def maketree(tree, location = os.getcwd(), exist_ok = False):
    location = str(location)

    for directory, value in six.iteritems(tree):
        path = osp.join(location, directory)
        makedirs(path, exist_ok = exist_ok)

        if isinstance(value, collections.Mapping):
            maketree(value, path, exist_ok = exist_ok)
        else:
            if value:
                path = osp.join(path, value)
                write(path, force = not exist_ok)

def check_port_available(port, host = "127.0.0.1", raise_err = False):
    """
    Check's whether a port is available or not.
    """
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result  = socket_.connect_ex((host, port))

    if result == 0:
        if raise_err:
            raise ccman.ValueError("Port {port} unavailable.".format(port = port))
        else:
            return False
    else:
        return True