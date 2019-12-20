# imports - compatibility imports
import six

# imports - standard imports
import collections

# imports - module imports
import ccman

def auto_typecast(value):
    str_to_bool = lambda x: { "True": True, "False": False, "None": None}[x]

    for type_ in (str_to_bool, int, float):
        try:
            return type_(value)
        except (KeyError, ValueError, TypeError):
            pass

    return value

def sequencify(value, type_ = list):
    if not isinstance(value, (list, tuple)):
        value = type_([value])
    return type_(value)

def merge_dict(*args):
    dict_ = ccman.Dict()
    
    for arg in args:
        copy = arg.copy()
        dict_.update(copy)
    
    return dict_

def dict_filter(dict_, filter_):
    result = dict((k, v) for k, v in six.iteritems(dict_) if v != filter_)
    return result

def list_filter(list_, filter_):
    result = list(filter(filter_, list_))
    return result

def dict_deep_update(d, u):
    # Shamelessly taken by: https://stackoverflow.com/a/3233356/6818563
    for k, v in six.iteritems(u):
        if isinstance(v, collections.Mapping):
            d[k] = dict_deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d