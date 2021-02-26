"""
Contains functions that implement the hash and encrypt processing.

.. function:: hash_password(password: str) -> str
    Hash password and return hash in str type
.. function:: verify_password(plain_password: str, hashed_password: str) -> bool
    Match input password with the hash
.. function:: generate_secret_key() -> bytes
    Generate secret key (might be used for cookie_storage)
"""

import base64

import bcrypt
import cryptography.fernet


def hash_password(password: str) -> str:
    """
    Hash password by bcrypt.

    :param password: plain password
    :type password: str

    :return: decoded hashed password
    :rtype: str
    """

    encoded_password = password.encode()
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(encoded_password,  salt)
    hashed_password = hashed_password_bytes.decode()

    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check to match of password and hash.

    :param plain_password: unhashed plain password
    :type plain_password: str
    :param hashed_password: hashed password from db
    :type hashed_password: str

    :return: status of matching
    :rtype: bool
    """

    plain_password = plain_password.encode()
    hashed_password = hashed_password.encode()
    result_status = bcrypt.checkpw(plain_password, hashed_password)

    return result_status


def generate_secret_key() -> bytes:
    """
    Generate secret key (might be used for session-cookie storage).

    :return: secret key
    :rtype: bytes
    """
    fernet_key = cryptography.fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    return secret_key
