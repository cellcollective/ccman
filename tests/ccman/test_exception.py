# imports - third-party imports
import pytest

# imports - module imports
import ccman

def test_exception():
    with pytest.raises(ccman.CCError):
        raise ccman.CCError

    assert isinstance(ccman.ValueError(), ccman.CCError)
    with pytest.raises(ccman.ValueError):
        raise ccman.ValueError

    assert isinstance(ccman.KeyError(),   ccman.CCError)
    with pytest.raises(ccman.KeyError):
        raise ccman.KeyError

    assert isinstance(ccman.NotImplementedError(), ccman.CCError)
    with pytest.raises(ccman.NotImplementedError):
        raise ccman.NotImplementedError
    
    assert isinstance(ccman.AuthenticationError(), ccman.CCError)
    with pytest.raises(ccman.AuthenticationError):
        raise ccman.AuthenticationError