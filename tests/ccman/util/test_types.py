# imports - module imports
from ccman.util.types import (
    auto_typecast,
    sequencify,
    merge_dict,
    dict_filter,
    list_filter
)

def test_auto_typecast():
    assert auto_typecast("foobar") == "foobar"
    assert auto_typecast("123456") == 123456
    assert auto_typecast("123.45") == 123.45

    assert auto_typecast("True")   == True
    assert auto_typecast("False")  == False
    assert auto_typecast("None")   == None

    assert auto_typecast(True)     == True
    assert auto_typecast(False)    == False
    assert auto_typecast(None)     == None

def test_sequencify():
    assert sequencify("foobar") == ["foobar"]
    assert sequencify([1,2,3])  == [1,2,3]
    assert sequencify([1,2,3])  != [3,2,1]
    assert sequencify([])       == []
    assert sequencify(None)     == [None]

    assert sequencify("foobar", type_ = tuple) == ("foobar",)
    assert sequencify([1,2,3],  type_ = tuple) == (1,2,3)
    assert sequencify([1,2,3],  type_ = tuple) != (3,2,1)
    assert sequencify([],       type_ = tuple) == tuple()
    assert sequencify(None,     type_ = tuple) == (None,)

def test_merge_dict():
    assert merge_dict({ "foo": "bar" }, { "bar": "baz" })     == { "foo": "bar", "bar": "baz" }
    assert merge_dict({ "foo": "bar" }, { "foo": "baz" })     == { "foo": "baz" }
    assert merge_dict({ 1: 2 }, { 3: 4 }, { 5: 6 }, { 7: 8 }) == { 1: 2, 3: 4, 5: 6, 7: 8 }
    assert merge_dict({ 1: 2 }, { 1: 3 }, { 1: 4 }, { 1: 1 }) == { 1: 1 }

def test_dict_filter():
    dict_ = { "foo": "bar", "bar": None }
    assert { "foo": "bar" } == dict_filter(dict_, None)

    dict_ = { "foo": "bar", "bar": "baz" }
    assert { "bar": "baz" } == dict_filter(dict_, "bar")

def test_list_filter():
    list_ = [1, 2, 3, 4, 5, 6, False]
    assert list_filter(list_, bool) == [1, 2, 3, 4, 5, 6]