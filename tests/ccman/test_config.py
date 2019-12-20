# imports - test imports
import pytest

# imports - module imports
from   ccman.config import check_key
import ccman

def test_check_key():
    assert check_key("test_config")       == ccman.Dict({ "name": "test_config", "crypt": False })
    assert check_key("test_crypt_config") == ccman.Dict({ "name": "test_crypt_config", "crypt": True })
    
    INVALID_KEY = "asdfghjklzx"

    with pytest.raises(ccman.KeyError):
        check_key(INVALID_KEY, raise_err = True)

    assert not check_key(INVALID_KEY, raise_err = False)

def test_get_config():
    pass