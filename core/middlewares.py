"""
Contains middlewares that wrap server work.


Classes {errors}:
    class ServerError(Exception):
    = catch any errors raised while the app working
    --------------------------------------------------------------------------------------------------------------------
Functions {decorators}:
    def create_error_middleware(overrides) -> Callable:
    = create error middleware
    --------------------------------------------------------------------------------------------------------------------
    def create_session_middleware() -> Callable:
    = create session middleware
    --------------------------------------------------------------------------------------------------------------------
Functions:
    async def handle_***(request) -> aiohttp.web.Response:
    = handle http error and return prepared template
    --------------------------------------------------------------------------------------------------------------------
    def setup_middlewares(app: aiohttp.web.Application) -> None:
    = setup all middlewares
    --------------------------------------------------------------------------------------------------------------------
"""

from typing import (
    Callable
)

import aiohttp.web
import aiohttp_session
import aiohttp_session.cookie_storage
import aiohttp_jinja2

from core import security


class ServerError(Exception):
    """ Catch any errors raised while the app working """


async def handle_401(request) -> aiohttp.web.Response:
    """ Handle http error {401 Unauthorized} and return response with prepared template """
    data = {
        'first_digit': 4,
        'second_digit': 0,
        'third_digit': 1,
        'message': 'Please, login first!'
    }
    return aiohttp_jinja2.render_template('error.html', request, data, status=401)


async def handle_403(request) -> aiohttp.web.Response:
    """ Handle http error {403 Forbidden} and return response with prepared template """
    data = {
        'first_digit': 4,
        'second_digit': 0,
        'third_digit': 3,
        'message': 'Sorry, but it is forbidden for you :)'
    }
    return aiohttp_jinja2.render_template('error.html', request, data, status=403)


async def handle_404(request) -> aiohttp.web.Response:
    """ Handle http error {404 Not Found} and return response with prepared template """
    data = {
        'first_digit': 4,
        'second_digit': 0,
        'third_digit': 4,
        'message': 'Hmm... We are lost!'
    }
    return aiohttp_jinja2.render_template('error.html', request, data, status=404)


async def handle_405(request) -> aiohttp.web.Response:
    """ Handle http error {405 Method Not Allowed} and return response with prepared template """
    data = {
        'first_digit': 4,
        'second_digit': 0,
        'third_digit': 5,
        'message': 'You on a wrong way! This method not allowed!'
    }
    return aiohttp_jinja2.render_template('error.html', request, data, status=405)


async def handle_500(request) -> aiohttp.web.Response:
    """ Handle http error {500 Internal Server Error} and return response with prepared template """
    data = {
        'first_digit': 5,
        'second_digit': 0,
        'third_digit': 0,
        'message': 'It is not you. It is me :) Sorry!'
    }
    return aiohttp_jinja2.render_template('error.html', request, data, status=500)


def create_error_middleware(overrides) -> Callable:
    """ Create error middleware """
    @aiohttp.web.middleware
    async def error_middleware(request, handler):
        """ Handle http errors and return particular error handler """
        try:
            return await handler(request)
        except aiohttp.web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)

            raise
        except ServerError:
            return await overrides[500](request)

    return error_middleware


def create_session_middleware() -> Callable:
    """ Create encrypted cookie storage """
    secret_key = security.generate_secret_key()
    cookie_storage = aiohttp_session.cookie_storage.EncryptedCookieStorage(secret_key)

    session_middleware = aiohttp_session.session_middleware(cookie_storage)
    return session_middleware


def setup_middlewares(app: aiohttp.web.Application) -> None:
    """ Setup all middlewares """
    error_middleware = create_error_middleware({
        404: handle_404,
        500: handle_500
    })

    session_middleware = create_session_middleware()

    app.middlewares.append(error_middleware)
    app.middlewares.append(session_middleware)
