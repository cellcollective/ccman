from ccman._compat import cmp

def test_cmp():
    assert cmp(1, 2) == -1
    assert cmp(2, 1) ==  1
    assert cmp(1, 1) ==  0