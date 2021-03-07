"""
Contains middlewares that wrap server work.

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
import pymysql

from . import security
from .database import db
from .views import (
    InvalidFormDataError,
    custom_errors
)
from .views.auth import AuthenticationError


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

        # it is invalid form data - it is the critical error for form data (that will be used in some processing)
        # (for difference between validation error and this check documentation)
        except InvalidFormDataError:
            if 400 in overrides:
                return await overrides[400](request)

            raise aiohttp.web.HTTPBadRequest
        # - - -

        # - - - - - - - - -

        # database errors (integrity errors, nonexistent data that saved in the database error) handling

        # # it is incorrect form data (try to relate nonexistent data) - invoke database integrity errors
        except pymysql.err.IntegrityError as error:
            if 400 in overrides:
                return await overrides[400](request)

            raise aiohttp.web.HTTPBadRequest
        # - - -

        # # it is not information in database (try to get nonexistent data) - record is not found
        except db.RecordNotFoundError:
            if 404 in overrides:
                return await overrides[404](request)
            raise aiohttp.web.HTTPNotFound
        # - - -

        # - - - - - - - - -

        # user access errors handling

        # # user is not verified - user has not access to action
        except AuthenticationError:
            if 403 in overrides:
                return await overrides[403](request)
            raise aiohttp.web.HTTPNotFound
        # - - -

        # - - - - - - - - -

        # custom errors handling

        # # handling custom http errors
        except aiohttp.web.HTTPException as error:
            override = overrides.get(error.status)
            if override:
                return await override(request)

            raise
        # - - -

        except Exception as error:
            request.app['logger'].error('Error raised while server is working with message: {}'.format(str(error)))
            request.app['logger'].exception(error)

            # debug - - |
            # raise
            # - - - - - |

            return await overrides[500](request)
        else:
            return handler_result

        # - - - - - - - - -

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
            request.app['logger'].info(message)

            raise error
        else:
            # pass static downloads
            if 'static' not in str(request.url):
                message = message.format(request.remote, str(request.url), request.method, 200)
                request.app['logger'].info(message)

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
    log_middleware = create_log_middleware()

    middlewares = [
        error_middleware,
        session_middleware,
        log_middleware
    ]

    app.middlewares.extend(middlewares)
