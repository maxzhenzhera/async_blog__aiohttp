"""
Contains functions that help with registering, authorizing and authentication.


Classes {errors}:
    class AuthenticationError(Exception):
    = raised when authentication is not satisfied
    --------------------------------------------------------------------------------------------------------------------
    class AuthorizationError(Exception):
    = raised when authorization is not satisfied
    --------------------------------------------------------------------------------------------------------------------
Functions:
    async def check_login_for_availability(request: aiohttp.web.Request, login: str) -> bool:
    = check login for availability (might be useful when new user is registering)
    --------------------------------------------------------------------------------------------------------------------
    async def authorize_user(request: aiohttp.web.Request, login: str, password: str) -> dict[str, Union[str, int]]:
    = authorize user, return user data (without user password)
    --------------------------------------------------------------------------------------------------------------------
    async def authenticate_user(request: aiohttp.web.Request, user_id: int) -> None:
    = authenticate user, return none but if user not authenticated raise error
    --------------------------------------------------------------------------------------------------------------------
"""

from typing import (
    Union
)

import aiohttp.web
import aiohttp_session
import aiomysql

from core.database import db
from core import security


class AuthenticationError(Exception):
    """ Raised when authentication is not satisfied """


class AuthorizationError(Exception):
    """ Raised when authorization is not satisfied """


async def check_login_for_availability(connection: aiomysql.Connection, login: str) -> bool:
    """ Check login for availability """
    status_of_login_availability = False

    try:
        _ = await db.fetch_one_user(connection, login=login)
    except db.RecordNotFoundError:
        status_of_login_availability = True

    return status_of_login_availability


async def authorize_user(connection: aiomysql.Connection, login: str, password: str) -> dict[str, Union[str, int]]:
    """
    Authorize user.
    Return user data (except password) if user authorized else raise errors.

    Raise:
        AuthorizationError      (if the given user data is not valid )
    """

    try:
        user = await db.fetch_one_user(connection, login=login)
    except db.RecordNotFoundError:
        message = 'user with the given login was not found'
        raise AuthorizationError(message)
    else:
        user_hashed_password = user['password']
        authorization_status = security.match_password_with_hash(
            password=password,
            hashed_password=user_hashed_password
        )

        if not authorization_status:
            message = 'the wrong password given'
            raise AuthorizationError(message)

    # user data will be saved in the session -> so, the password removed from this data
    del user['password']

    return user


async def authenticate_user(request: aiohttp.web.Request, user_id: int) -> None:
    """
    Conform that given user id (might be the owner of post, note) correspond to user id in the session.

    Raise:
        AuthenticationError     (if the given user-id and session user-id do not correspond)
    """

    session = await aiohttp_session.get_session(request)
    session_user_id = session['user']['id']

    if user_id != session_user_id:
        message = 'given user-id does not correspond to session user-id'
        raise AuthenticationError(message)
