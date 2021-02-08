"""
Contains functions that implement the hash and encrypt processing.


Functions:
    def hash_password(password: str) -> str:
    = hash password and return hash in str type
    --------------------------------------------------------------------------------------------------------------------
    def match_password_with_hash(password: str, hashed_password: str) -> bool:
    = match input password with the hash
    --------------------------------------------------------------------------------------------------------------------
    def generate_secret_key() -> bytes:
    = generate secret key (might be used for cookie_storage)
    --------------------------------------------------------------------------------------------------------------------
"""

import base64
import bcrypt
import cryptography.fernet


def hash_password(password: str) -> str:
    """ Hash password by bcrypt """
    encoded_password = password.encode()
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(encoded_password,  salt)
    hashed_password = hashed_password_bytes.decode()
    return hashed_password


def match_password_with_hash(password: str, hashed_password: str) -> bool:
    """ Check the password on compliance with the hash """
    password = password.encode()
    hashed_password = hashed_password.encode()
    result_status = bcrypt.checkpw(password, hashed_password)
    return result_status


def generate_secret_key() -> bytes:
    """ Generate secret key (might be used for session-cookie storage) """
    fernet_key = cryptography.fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    return secret_key
