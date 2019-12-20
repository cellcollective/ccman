# imports - third-party imports
import pytest

# imports - module imports
from ccman.util.crypto import generate_hash, encrypt, decrypt

def test_encrypt_decrypt():
    assert decrypt(encrypt("foobar")) == "foobar"
    assert decrypt(encrypt("abcdef")) == "abcdef"

    assert not encrypt("foobar") == "foobar"

    with pytest.raises(Exception):
        decrypt("foobar")

def test_generate_hash():
    assert generate_hash()         != generate_hash()
    assert generate_hash("foobar") == generate_hash("foobar")

    assert generate_hash()         != generate_hash("foobar")

    assert len(generate_hash())                 == 40
    assert len(generate_hash(type_ = "md5"))    == 32
    assert len(generate_hash(type_ = "sha256")) == 64