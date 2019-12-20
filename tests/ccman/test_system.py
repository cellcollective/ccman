# imports - standard imports
import sys
import os
import os.path as osp
import subprocess

# imports - third-party imports
from   distutils.spawn import find_executable
import pytest

# imports - module imports
from   ccman.system    import (read, write, link, popen, which, pardir, makedirs, remove,
    maketree, check_port_available)
import ccman

def test_read(tmpdir):
    directory = tmpdir.mkdir("tmp")
    tempfile  = directory.join("foobar.txt")
    tempfile.write("foobar")

    assert tempfile.read() == read(tempfile)

    tempfile  = directory.join("barfoo.txt")
    tempfile.write(\
    """
    foobar
    \n
    barfoo
    """
    )

    assert tempfile.read() == read(tempfile)

def test_write(tmpdir):
    directory  = tmpdir.mkdir("tmp")
    tempfile   = directory.join("foobar.txt")
    
    prev, next = "foobar", "barfoo"

    write(tempfile, prev)
    assert tempfile.read() == prev

    write(tempfile, next)
    assert tempfile.read() == prev

    write(tempfile, next, force = True)
    assert tempfile.read() == next

def test_link(tmpdir):
    directory1 = tmpdir.mkdir("tmp1")
    directory2 = osp.join(str(directory1), "tmp2")
    link(directory1, directory2)

    assert osp.islink(directory2)
    assert osp.isdir(directory2)

    tempfile1  = directory1.join("foobar.txt")
    tempfile2  = osp.join(str(directory1), "barfoo.txt")
    link(tempfile1, tempfile2)

    assert osp.islink(tempfile2)

    link(tempfile1, tempfile2, exist_ok = True)
    assert osp.islink(tempfile2)

    with pytest.raises(OSError) as e:
        link(tempfile1, tempfile2)

def test_popen(tmpdir):
    directory = tmpdir.mkdir("tmp")

    string    = "Hello, World!"

    code, out, err = popen("echo '{string}'".format(
        string = string
    ), output = True)
    assert code == 0
    assert out  == string
    assert not err
    
    env = ccman.Dict({ "FOOBAR": "foobar" })
    code, out, err = popen("echo $FOOBAR; echo $PATH",
        output = True, env = env)
    assert code == 0
    assert out  == "{}\n{}".format(env.FOOBAR, os.environ["PATH"])
    assert not err

    with pytest.raises(ccman.PopenError):
        code = popen("exit 42")

    errstr = "foobar"
    code, out, err = popen('python -c "raise Exception("{errstr}")"'.format(errstr = errstr),
        output = True, raise_err = False)
    assert code == 1
    assert not out
    assert errstr in err

    filename = "foobar.txt"
    popen("touch {filename}".format(filename = filename), cwd = str(directory))
    assert osp.exists(osp.join(str(directory), filename))

def test_which():
    assert which("foobar") == None
    assert which(sys.executable) == find_executable(sys.executable)

    with pytest.raises(ccman.ValueError) as e:
        which("foobar", raise_err = True)
    assert "executable not found" in str(e.value)

def test_pardir():
    assert pardir(__file__)    == osp.dirname(__file__)
    assert pardir(__file__, 2) == osp.dirname(osp.dirname(__file__))

def test_makedirs(tmpdir):
    directory = tmpdir.mkdir("tmp")
    path      = osp.join(str(directory), "foo", "bar")

    makedirs(path)
    assert osp.exists(path)

    makedirs(path, exist_ok = True)
    assert osp.exists(path)

    with pytest.raises(OSError):
        makedirs(path)

def test_remove(tmpdir):
    directory  = tmpdir.mkdir("tmp")
    tempfile   = directory.join("foobar.txt")
    tempfile.write("foobar")

    remove(tempfile)
    assert not osp.exists(str(tempfile))

    with pytest.raises(OSError) as e:
        remove(tempfile)
    
    remove(tempfile, raise_err = False)
    assert not osp.exists(str(tempfile))

    with pytest.raises(OSError) as e:
        remove(directory)

    remove(directory, raise_err = False)
    assert osp.exists(str(directory))

    remove(directory, recursive = True)
    assert not osp.exists(str(directory))

def test_maketree(tmpdir):
    directory = tmpdir.mkdir("tmp")
    tree      = dict(foo = dict(bar = "baz"))
    
    maketree(tree, location = directory)
    assert osp.exists(osp.join(str(directory), "foo", "bar", "baz"))

    with pytest.raises(OSError) as e:
        maketree(tree, location = directory)

    maketree(tree, location = directory, exist_ok = True)
    assert osp.exists(osp.join(str(directory), "foo", "bar", "baz"))

def test_check_port_available(server):
    assert check_port_available(8000) == True

    server.run(port = 8000, thread = True)
    assert check_port_available(8000) == False

    with pytest.raises(ccman.ValueError):
        check_port_available(8000, raise_err = True)