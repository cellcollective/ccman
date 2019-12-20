def strip(string):
    string = string.lstrip()
    string = string.rstrip()
    return string

def safe_encode(string, encoding = "utf-8"):
    encoded = string
    
    try:
        encoded = string.encode(encoding)
    except AttributeError:
        pass

    return encoded

def safe_decode(object_, encoding = "utf-8"):
    decoded = object_
    
    try:
        decoded = object_.decode(encoding)
    except AttributeError:
        pass

    return decoded