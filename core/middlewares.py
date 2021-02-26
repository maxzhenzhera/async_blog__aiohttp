"""
Contains middlewares that wrap server work.


.. exception:: ServerError(Exception)
    catch any errors raised while the app working


.. function:: create_error_middleware(overrides) -> Callable
    create error middleware
.. function:: create_session_middleware() -> Callable
    create session middleware
.. function:: create_log_middleware() -> Callable
    create log middleware
.. function:: setup_middlewares(app: aiohttp.web.Application) -> None
    setup all middlewares
"""

from typing import (
    Any,
    Callable
)

import aiohttp.web
import aiohttp_session
import aiohttp_session.cookie_storage
from loguru import logger

from . import security
from .database import db
from .views import custom_errors
from .views.auth import AuthenticationError


class ServerError(Exception):
    """ Catch any errors raised while the app working """


def create_error_middleware(overrides: dict[int, Callable]) -> Callable:
    """
    Create error middleware.

    :param overrides: mapping of pairs [http_code: error_handler]
    :type overrides: dict[int, Callable]

    :return: middleware
    :rtype: Callable
    """

    @aiohttp.web.middleware
    async def error_middleware(request: aiohttp.web.Request, handler: Callable) -> Any:
        """
        Handle errors and return custom error page if handled error was caught.

        :param request: requests
        :type request: aiohttp.web.Request
        :param handler: view function
        :type handler: Callable

        :return: handler result or custom error page
        :rtype: Any
        """

        try:
            handler_result = await handler(request)

        # it is not information in database - record is not found
        except db.RecordNotFoundError:
            if 404 in overrides:
                return await overrides[404](request)
            raise aiohttp.web.HTTPNotFound
        # - - -

        # user is not verified - user has not access to action
        except AuthenticationError:
            raise aiohttp.web.HTTPForbidden
        # - - -

        # handling custom http errors
        except aiohttp.web.HTTPException as error:
            override = overrides.get(error.status)
            if override:
                return await override(request)
        # - - -

            # debug mod
            raise

        # except ServerError:
        #     return await overrides[500](request)
        else:
            return handler_result

    return error_middleware


def create_session_middleware() -> Callable:
    """
    Create session middleware.

    :return: middleware
    :rtype: Callable
    """

    secret_key = security.generate_secret_key()
    cookie_storage = aiohttp_session.cookie_storage.EncryptedCookieStorage(secret_key)

    session_middleware = aiohttp_session.session_middleware(cookie_storage)

    return session_middleware


def create_log_middleware() -> Callable:
    """
    Create log middleware.

    :return: middleware
    :rtype: Callable
    """

    @aiohttp.web.middleware
    async def log_middleware(request: aiohttp.web.Request, handler: Callable) -> Any:
        """

        :param request: request
        :type request:
        :param handler: view function
        :type handler: Callable

        :return: handler result
        :rtype: Any

        :raises aiohttp.web.HTTPException: raised if any http error was caught (while view function produce result)
        """

        message = "TRAFFIC LOG:\n"
        message += ('=' * 124) + '\n'
        message += f"{'FROM':^30}|{'TO':^70}|{'WITH':^10}|{'CODE':^10}|\n"
        message += ('=' * 124) + '\n'
        message += "{:^30}|{:^70}|{:^10}|{:^10}|\n"
        message += ('=' * 124) + '\n'

        try:
            handler_result = await handler(request)
        except aiohttp.web.HTTPException as error:
            message = message.format(request.remote, str(request.url), request.method, error.status)
            logger.info(message)

            raise error
        else:
            # pass static downloads
            if 'static' not in request:
                message = message.format(request.remote, str(request.url), request.method, 200)
                logger.info(message)

            return handler_result

    return log_middleware


def setup_middlewares(app: aiohttp.web.Application) -> None:
    """
    Setup all middlewares.

    :param app: instance of the web application
    :type app: aiohttp.web.Application

    :return: None
    :rtype: None
    """

    error_middleware = create_error_middleware(overrides=custom_errors.errors)
    session_middleware = create_session_middleware()
    # log_middleware = create_log_middleware()

    middlewares = [
        error_middleware,
        session_middleware,
        # log_middleware
    ]

    app.middlewares.extend(middlewares)
