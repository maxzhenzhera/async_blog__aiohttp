"""
Contains registration and authorization implementations.

.. exception:: AuthorizationError(UserAccessError)
    Raised when authorization is not satisfied
.. exception:: RegistrationError(UserAccessError)
    Raised when registration data is improper (busy login, incorrect data)

.. function:: _get_user_group_id(user_data: dict) -> int
    Return user group id by user data
.. function:: check_login_for_availability(connection: aiomysql.Connection, login: str, *args,
        except_user_id: Optional[int] = None) -> bool
    Return status of login availability
.. function:: register_user(connection: aiomysql.Connection, user_form_data: validators.UserCreation, *args,
        user_is_admin: bool = False) -> None
    Register user (add user in db)
.. function:: authorize_user(connection: aiomysql.Connection, request: aiohttp.web.Request,
        user_form_data: Union[validators.UserAuthorization, validators.UserCreation]) -> None
    Authorize user (set user data in the session)
.. function:: logout_user(request: aiohttp.web.Request) -> None
    Logout user (clear the session)
"""

from typing import (
    Optional,
    Type,
    Union
)

import aiohttp.web
import aiohttp_session
import aiomysql

from . import user_groups
from .errors import UserAccessError
from ... import security
from ...database import (
    db,
    validators
)


class AuthorizationError(UserAccessError):
    """ Raised when authorization is not satisfied """


class RegistrationError(UserAccessError):
    """ Raised when registration data is improper (busy login, incorrect data) """


def _get_user_group_id(user_data: dict) -> int:
    """
    Compute user group by user db data.

    :param user_data: user data from db
    :type user_data: dict

    :return: user grant (role)
    :rtype: Type[user_groups.UserGroup]
    """

    # nice crutch ...

    # user
    user_group_id = user_groups.USER_USER_GROUP_ID
    if user_data['is_moderator']:
        # moderator
        user_group_id = user_groups.MODERATOR_USER_GROUP_ID
    if user_data['is_admin']:
        # admin
        user_group_id = user_groups.ADMIN_USER_GROUP_ID

    return user_group_id


async def check_login_for_availability(connection: aiomysql.Connection, login: str, *args,
                                       except_user_id: Optional[int] = None
                                       ) -> bool:
    """
    Check login for availability.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param login: login given in registration form
    :type login: str
    :keyword except_user_id: if found user will have the same id - function will return True status.
    :type except_user_id: Optional[int]

    :return: status of availability
    :rtype: bool
    """

    status_of_login_availability = False

    try:
        user = await db.fetch_one_user(connection, login=login)
    except db.RecordNotFoundError:
        status_of_login_availability = True
    else:
        if except_user_id:
            user_id = user['id']
            if user_id == except_user_id:
                status_of_login_availability = True

    return status_of_login_availability


async def register_user(connection: aiomysql.Connection, user_form_data: validators.UserCreation, *args,
                        user_is_admin: bool = False) -> None:
    """
    Register user_form_data.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param user_form_data: registration form data
    :type user_form_data: validators.UserCreation
    :param user_is_admin: with this flag will be registered user with admin grant
    :type user_is_admin: bool

    :return: None
    :rtype: None

    :raises RegistrationError: raised if login is busy
    """

    login_availability = await check_login_for_availability(connection, user_form_data.login)

    if login_availability:
        hashed_password = security.hash_password(user_form_data.password)
        user_with_hashed_password = validators.UserCreation(login=user_form_data.login, password=hashed_password)

        await db.insert_user(connection, user_with_hashed_password, user_is_admin=user_is_admin)
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
    user_group_id = _get_user_group_id(user_db_data)
    session['user']['group_id'] = user_group_id


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
