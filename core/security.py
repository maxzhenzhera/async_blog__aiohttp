"""
Contains functions that implement the hash and encrypt processing.

Functions:
    --------------------------------------------------------------------------------------------------------------------
        ...
    --------------------------------------------------------------------------------------------------------------------
"""

import base64
import bcrypt
import cryptography.fernet


def hash_password(password: str) -> str:
    """ Hash input data by bcrypt """
    encoded_password = password.encode()
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(encoded_password,  salt)
    hashed_password = hashed_password_bytes.decode()
    print(hashed_password)
    print(type(hashed_password))
    return hashed_password


def compare_password_with_hash(password: str, hashed_password: str) -> bool:
    """ Check the password on compliance with the hash """
    password = password.encode()
    hashed_password = hashed_password.encode()

    if bcrypt.checkpw(password, hashed_password):
        print("It Matches!")
        return False
    else:
        print("It Does not Match :(")
        return True


def generate_secret_key() -> bytes:
    """ Generate secret key for session-cookie storage """
    fernet_key = cryptography.fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    return secret_key


# if __name__ == '__main__':
#     password = 'super_secret_key'
#     hashed_password = hash_password(password)
#     compare_password_with_hash(password, hashed_password)
