"""
Contains authentication policy (functions that verify personality).

.. exception:: AuthenticationError(UserAccessError)
    Raised when authentication is not satisfied

.. function:: authenticate_user_by_password(request: aiohttp.web.Request, password: str) -> dict
    Authenticate user by password
.. function:: authenticate_post_owner(request: aiohttp.web.Request, post_id: int) -> tuple[int, dict]
    Authenticate post owner
.. function:: authenticate_note_rubric_owner(request: aiohttp.web.Request, note_rubric_id: int) -> tuple[int, dict]
    Authenticate note rubric owner
.. function:: authenticate_note_owner(request: aiohttp.web.Request, note_id: int) -> tuple[int, dict]
    Authenticate note owner
"""

import aiohttp.web

from .errors import UserAccessError
from .. import (
    InvalidFormDataError,
    helpers,
    utils
)
from ... import security
from ...database import db


class AuthenticationError(UserAccessError):
    """ Raised when authentication is not satisfied """


async def authenticate_user_by_password(request: aiohttp.web.Request, password: str) -> dict:
    """
    Authenticate user by password, return user data.

    :param request: request
    :type request: aiohttp.web.Request
    :param password: plain given password
    :type password: str

    :return: user data
    :rtype: dict

    :raises AuthenticationError: if authentication is not verified
    """

    session_user_id = await helpers.get_user_id_from_session(request)

    async with request.app['db'].acquire() as connection:
        session_user = await db.fetch_one_user(connection, user_id=session_user_id)
    session_user_hashed_password = session_user['password']

    authentication_status = security.verify_password(password, session_user_hashed_password)
    if not authentication_status:
        message = 'the given password is wrong'
        raise AuthenticationError(message)

    return session_user


@utils.handle_local_error(except_error=db.RecordNotFoundError, raise_error=InvalidFormDataError)
async def authenticate_post_owner(request: aiohttp.web.Request, post_id: int) -> tuple[int, dict]:
    """
    Authenticate post owner, return post data.

    :param request: request
    :type request: aiohttp.web.Request
    :param post_id: post id
    :type post_id: int

    :return: tuple (session_user_id, post_data)
    :rtype: tuple[int, dict]

    :raises AuthenticationError: if authentication is not verified
    """

    async with request.app['db'].acquire() as connection:
        post = await db.fetch_one_post(connection, post_id)

    post_owner_id = post['user_id']

    session_user_id = await helpers.get_user_id_from_session(request)

    if post_owner_id != session_user_id:
        raise AuthenticationError

    return (session_user_id, post)


@utils.handle_local_error(except_error=db.RecordNotFoundError, raise_error=InvalidFormDataError)
async def authenticate_note_rubric_owner(request: aiohttp.web.Request, note_rubric_id: int) -> tuple[int, dict]:
    """
    Authenticate note rubric owner, return note rubric data.

    :param request: request
    :type request: aiohttp.web.Request
    :param note_rubric_id: note rubric id
    :type note_rubric_id: int

    :return: tuple (session_user_id, note_rubric_data)
    :rtype: tuple[int, dict]

    :raises AuthenticationError: if authentication is not verified
    :raises aiohttp.web.HTTPBadRequest: if process work with nonexistence db record
    """

    async with request.app['db'].acquire() as connection:
        note_rubric = await db.fetch_one_note_rubric(connection, note_rubric_id)

    note_rubric_owner_id = note_rubric['user_id']

    session_user_id = await helpers.get_user_id_from_session(request)

    if note_rubric_owner_id != session_user_id:
        raise AuthenticationError

    return (session_user_id, note_rubric)


@utils.handle_local_error(except_error=db.RecordNotFoundError, raise_error=InvalidFormDataError)
async def authenticate_note_owner(request: aiohttp.web.Request, note_id: int) -> tuple[int, dict]:
    """
    Authenticate note owner, return note data.

    :param request: request
    :type request: aiohttp.web.Request
    :param note_id: note rubric id
    :type note_id: int

    :return: tuple (session_user_id, note_data)
    :rtype: tuple[int, dict]

    :raises AuthenticationError: if authentication is not verified
    :raises aiohttp.web.HTTPBadRequest: if process work with nonexistence db record
    """

    async with request.app['db'].acquire() as connection:
        note = await db.fetch_one_note(connection, note_id)

    note_owner_id = note['user_id']

    session_user_id = await helpers.get_user_id_from_session(request)

    if note_owner_id != session_user_id:
        raise AuthenticationError

    return (session_user_id, note)
