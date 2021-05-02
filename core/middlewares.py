"""
Contains middlewares that wrap server work.

.. function:: create_error_middleware(overrides) -> Callable
    create error middleware
.. function:: create_session_redis_storage() -> RedisStorage
    create session redis storage
.. function:: create_log_middleware() -> Callable
    create log middleware
.. function:: setup_middlewares(app: aiohttp.web.Application) -> None
    setup all middlewares
"""

import logging
from typing import (
    Any,
    Callable
)

import aiohttp.web
from aiohttp_session.redis_storage import RedisStorage
import aioredis
import pymysql

from .settings import REDIS_ADDRESS
from .database import db
from .views import (
    InvalidFormDataError,
    custom_errors
)
from .views.auth import AuthenticationError


logger = logging.getLogger(__name__)


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
            logger.exception(msg=f'Error raised while server is working: {error}', exc_info=error)

            # debug - - |
            # raise
            # - - - - - |

            return await overrides[500](request)
        else:
            return handler_result

        # - - - - - - - - -

    return error_middleware


async def create_session_redis_storage() -> RedisStorage:
    """
    Create session redis storage.

    For redis pool creation `await` - async function is required.
    Middleware setup moved in async `init_app` function.

    :return: middleware
    :rtype: Callable
    """

    redis_pool = await aioredis.create_redis_pool(REDIS_ADDRESS)

    logger.info('Redis session storage has been set!')

    session_redis_storage = RedisStorage(redis_pool)

    return session_redis_storage


def setup_middlewares(app: aiohttp.web.Application) -> None:
    """
    Setup all middlewares.

    :param app: instance of the web application
    :type app: aiohttp.web.Application

    :return: None
    :rtype: None
    """

    error_middleware = create_error_middleware(overrides=custom_errors.errors)

    middlewares = [
        error_middleware,
    ]

    app.middlewares.extend(middlewares)
