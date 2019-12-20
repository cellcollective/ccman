# imports - standard imports
import json

# imports - module imports
from ccman.util.json import read, write, update

def test_read(tmpdir):
    directory = tmpdir.mkdir("tmp")
    tempfile  = directory.join("foobar.json")
    tempfile.write('{ "foo": "bar" }')

    assert read(tempfile) == dict(foo = "bar")

def test_write(tmpdir):
    directory = tmpdir.mkdir("tmp")
    tempfile  = directory.join("foobar.json")
    
    data1 = dict(foo = "bar")
    write(tempfile, data1)

    assert read(tempfile) == data1

    data2 = dict(bar = "foo")
    write(tempfile, data2)

    assert read(tempfile) == data1

    write(tempfile, data2, force = True)
    assert read(tempfile) == data2

def test_update(tmpdir):
    directory = tmpdir.mkdir("tmp")
    tempfile  = directory.join("foobar.json")

    data = dict(foo = "bar")
    write(tempfile, data)

    data = dict(foo = "foo")
    update(tempfile, data)
    
    assert read(tempfile) == dict(foo = "foo")

    update(tempfile, dict(bar = "bar"))

    assert read(tempfile) == dict(
        foo = "foo",
        bar = "bar"
    )