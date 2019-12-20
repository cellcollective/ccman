# imports - standard imports
import os

# imports - third-party imports
import pytest

# imports - module imports
from   ccman.environment import getenv, setenv, getenvvar, PREFIX
from   ccman.util.crypto import generate_hash
import ccman

def test_getenvvar():
    hash_ = generate_hash()
    sep   = "_"
    key   = "%s%s%s" % (PREFIX, sep, hash_)

    assert key == getenvvar(hash_)

    sep   = "-"
    key   = "%s%s%s" % (PREFIX, sep, hash_)
    
    assert key == getenvvar(hash_, seperator = sep)

def test_setenv():
    key = generate_hash()
    val = generate_hash()

    setenv(key, val)

    assert os.environ[getenvvar(key)] == val

def test_getenv():
    key = generate_hash()
    val = generate_hash()

    setenv(key, val)

    assert getenv(key) == val
    
    with pytest.raises(ccman.KeyError):
        getenv(generate_hash(), raise_err = True)

    assert getenv(generate_hash()) == None
    
    new = 5000
    setenv(key, new)

    assert val == getenv(key, cast = False)
    assert val == getenv(key)

    setenv(key, new, force = True)
    
    assert "5000" == getenv(key, cast = False)
    assert  5000  == getenv(key)