"""
Django's crypto utilities.
"""
import hashlib
import hmac


def salted_hmac(key_salt, value, secret, algorithm='sha256'):
    """
    Return the HMAC of 'value', using a key generated from key_salt and a
    secret (which defaults to settings.SECRET_KEY). Default algorithm is SHA256,
    but any algorithm name supported by hashlib can be passed.

    A different key_salt should be passed in for every application of HMAC.
    """
    key_salt = key_salt.encode()
    secret = secret.encode()
    value = value.encode()
    
    # We need to generate a derived key from our base key. We can do this by
    # passing the key_salt and our base key through a pseudo-random function.
    key = hashlib.new(algorithm, key_salt + secret).digest()
    
    # We use HMAC to generate the hash
    return hmac.new(key, msg=value, digestmod=algorithm)


def constant_time_compare(val1, val2):
    """
    Return True if the two strings are equal, False otherwise.
    
    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0
