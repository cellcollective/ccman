class CCError(Exception):
    pass

class KeyError(CCError):
    pass

class ValueError(CCError):
    pass

class NotImplementedError(CCError):
    pass

class AuthenticationError(CCError):
    pass

class DataBaseError(CCError):
    pass

class PopenError(CCError):
    pass