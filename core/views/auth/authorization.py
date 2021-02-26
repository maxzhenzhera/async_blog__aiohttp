"""
Contains registration and authorization implementations.

.. exception:: AuthorizationError(UserAccessError)
    Raised when authorization is not satisfied
.. exception:: RegistrationError(UserAccessError)
    Raised when registration data is improper (busy login, incorrect data)

.. function:: _get_user_grant(user_data: dict) -> Type[user_groups.UserGroup]
    Return user grant that based on user db data
.. function:: _check_login_for_availability(connection: aiomysql.Connection, login: str) -> bool
    Return status of login availability
.. function:: register_user(connection: aiomysql.Connection, user_form_data: validators.UserCreation) -> None
    Add user in db (register)
.. function:: authorize_user(request: aiohttp.web.Request, user_form_data: validators.UserCreation) -> None
    Set user data in the session
.. function:: logout_user(request: aiohttp.web.Request) -> None
    Clear session user data
"""

from typing import (
    Type,
    Union
)

import aiohttp.web
import aiohttp_session
import aiomysql

from . import user_groups
from .error import UserAccessError
from ... import security
from ...database import (
    db,
    validators
)


class AuthorizationError(UserAccessError):
    """ Raised when authorization is not satisfied """


class RegistrationError(UserAccessError):
    """ Raised when registration data is improper (busy login, incorrect data) """


def _get_user_group(user_data: dict) -> Type[user_groups.UserGroup]:
    """
    Compute user group by user db data.

    :param user_data: user data from db
    :type user_data: dict

    :return: user grant (role)
    :rtype: Type[user_groups.UserGroup]
    """

    user_grant = user_groups.User
    if user_data['is_moderator']:
        user_grant = user_groups.Moderator
    if user_data['is_admin']:
        user_grant = user_groups.Admin

    return user_grant


async def _check_login_for_availability(connection: aiomysql.Connection, login: str) -> bool:
    """
    Check login for availability.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param login: login given in registration form
    :type login: str

    :return: status of availability
    :rtype: bool
    """

    status_of_login_availability = False

    try:
        _ = await db.fetch_one_user(connection, login=login)
    except db.RecordNotFoundError:
        status_of_login_availability = True

    return status_of_login_availability


async def register_user(connection: aiomysql.Connection, user_form_data: validators.UserCreation) -> None:
    """
    Register user_form_data.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param user_form_data: registration form data
    :type user_form_data: validators.UserCreation

    :return: None
    :rtype: None

    :raises RegistrationError: raised if login is busy
    """

    login_availability = await _check_login_for_availability(connection, user_form_data.login)

    if login_availability:
        hashed_password = security.hash_password(user_form_data.password)
        user_with_hashed_password = validators.UserCreation(login=user_form_data.login, password=hashed_password)

        await db.insert_user(connection, user_with_hashed_password)
    else:
        message = 'Login is busy. Choose another, please!'
        raise RegistrationError(message)


async def authorize_user(connection: aiomysql.Connection, request: aiohttp.web.Request,
                         user_form_data: Union[validators.UserAuthorization, validators.UserCreation]
                         ) -> None:
    """
    Authorize user (check user data, set user data in session).

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param request: request (to get session)
    :type request: aiohttp.web.Request
    :param user_form_data: authorization form data
    :type user_form_data: Union[validators.UserAuthorization, validators.UserCreation]

    :return: None
    :rtype: None

    :raises AuthorizationError: raised if the given user data do not correspond db data
    """

    try:
        user_db_data = await db.fetch_one_user(connection, login=user_form_data.login)
    except db.RecordNotFoundError:
        message = 'user with the given login was not found'
        raise AuthorizationError(message)
    else:
        user_hashed_password = user_db_data['password']
        authorization_status = security.verify_password(
            plain_password=user_form_data.password,
            hashed_password=user_hashed_password
        )

        if not authorization_status:
            message = 'the wrong password given'
            raise AuthorizationError(message)

    # user data will be saved in the session -> so, the password removed from this data
    del user_db_data['password']

    # set user data in new session
    session = await aiohttp_session.new_session(request)
    session['user'] = user_db_data

    # set user grant in the session
    user_grant = _get_user_group(user_db_data)
    session['user']['group'] = user_grant


async def logout_user(request: aiohttp.web.Request) -> None:
    """
    Clear all user session data.

    :param request: request (to get session)
    :type request: aiohttp.web.Request

    :return: None
    :rtype: None
    """

    session = await aiohttp_session.get_session(request)
    session.invalidate()
