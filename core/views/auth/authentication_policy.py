"""
Contains authentication policy (functions that verify personality).

.. exception:: AuthenticationError(UserAccessError)
    Raised when authentication is not satisfied

.. function:: async def authenticate_post_owner(request: aiohttp.web.Request, post_id: int) -> tuple[int, dict]
    Authenticate post owner
.. function:: async def authenticate_note_rubric_owner(request: aiohttp.web.Request, note_rubric_id: int
        ) -> tuple[int, dict]
    Authenticate note rubric owner
.. function:: async def authenticate_note_owner(request: aiohttp.web.Request, note_id: int) -> tuple[int, dict]
    Authenticate note owner
"""

import aiohttp.web
import aiohttp_session

from .error import UserAccessError
from ...database import db


class AuthenticationError(UserAccessError):
    """ Raised when authentication is not satisfied """


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

    session = await aiohttp_session.get_session(request)
    session_user_id = session['user']['id']

    if post_owner_id != session_user_id:
        raise AuthenticationError

    return (session_user_id, post)


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
    """

    async with request.app['db'].acquire() as connection:
        note_rubric = await db.fetch_one_note_rubric(connection, note_rubric_id)
    note_rubric_owner_id = note_rubric['user_id']

    session = await aiohttp_session.get_session(request)
    session_user_id = session['user']['id']

    if note_rubric_owner_id != session_user_id:
        raise AuthenticationError

    return (session_user_id, note_rubric)


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
    """

    async with request.app['db'].acquire() as connection:
        note = await db.fetch_one_note(connection, note_id)
    note_owner_id = note['user_id']

    session = await aiohttp_session.get_session(request)
    session_user_id = session['user']['id']

    if note_owner_id != session_user_id:
        raise AuthenticationError

    return (session_user_id, note)
