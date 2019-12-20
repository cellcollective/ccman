# imports - compatibility imports
import six

# imports - standard imports
import uuid
import hashlib

# imports - third-party imports
from   cryptography.fernet import Fernet

# imports - module imports
from   ccman.util.string import (
    safe_encode,
    safe_decode
)
import ccman

def generate_hash(string = None, type_ = 'sha1'):
    string = string or str(uuid.uuid4())
    string = string.encode('utf-8')

    algo   = getattr(hashlib, type_)()
    algo.update(string)

    digest = algo.hexdigest()

    return digest

def _generate_secret_key():
    key    = Fernet.generate_key()

    result = ccman.db["tabSingle"].find_one(key = "secret_key")

    if not result:
        ccman.db["tabSingle"].insert(dict(
            key   = "secret_key",
            value = key
        ))
    else:
        key = result["value"]

    return key

def encrypt(objekt):
    key     = _generate_secret_key()
    key     = safe_encode(key)
    cipher  = Fernet(key)

    encoded = safe_encode(objekt)
    encrypt = cipher.encrypt(encoded)
    decoded = safe_decode(encrypt)

    return decoded

def decrypt(objekt):
    key     = _generate_secret_key()
    key     = safe_encode(key)
    cipher  = Fernet(key)

    encoded = safe_encode(objekt)
    decrypt = cipher.decrypt(encoded)
    decoded = safe_decode(decrypt)

    return decoded