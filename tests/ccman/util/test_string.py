# imports - third-party imports
import pytest

# imports - module imports
from ccman.util.string import strip, safe_encode, safe_decode

def test_strip():
    string = "foobar"
    assert strip(string) == string

    string = "\n   foobar\nfoobar   \n   "
    assert strip(string) == "foobar\nfoobar"

    string = "\n\n\n"
    assert strip(string) == ""

    string = "\r\nfoobar\nfoobar\n"
    assert strip(string) == "foobar\nfoobar"

def test_safe_encode():
    assert safe_encode(b"foobar") == b"foobar"
    assert safe_encode( "foobar") == b"foobar"

    assert safe_encode(123456789) == 123456789

def test_safe_decode():
    assert safe_decode(b"foobar") == "foobar"
    assert safe_decode( "foobar") == "foobar"
    
    assert safe_encode(123456789) == 123456789