"""
Stub module for PyJWT to satisfy imports without installing the package.
"""


class PyJWTError(Exception):
    """Dummy exception for JWT errors"""

    pass


def encode(payload, secret, algorithm=None):
    """Dummy encode: returns string representation of payload"""
    return str(payload)


def decode(token, secret, algorithms=None, options=None):
    """Dummy decode: attempts to evaluate token as Python literal or returns empty dict"""
    try:
        return eval(token)
    except Exception:
        return {}
