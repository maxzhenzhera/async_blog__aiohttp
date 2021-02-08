"""
Contains functions that help handle and finalize view result


Functions {decorators}:
    def put_session_data_in_view_result(handler: Callable) -> Callable:
    = put all session data in result of a view handler
    --------------------------------------------------------------------------------------------------------------------
    def put_routes_in_view_result(handler: Callable) -> Callable:
    = put app routes in result of a view handler
    --------------------------------------------------------------------------------------------------------------------
"""

from collections.abc import (
    Mapping
)
from functools import wraps
from typing import (
    Callable

)

import aiohttp.web
import aiohttp_session


def put_session_data_in_view_result(handler: Callable) -> Callable:
    """ Put in handler result session data """
    @wraps(handler)
    async def inner(request: aiohttp.web.Request, *args, **kwargs) -> dict:
        """ Get session by request and put it in handler result data """
        session = await aiohttp_session.get_session(request)
        handler_result: dict = await handler(request)
        # put session data in handler result
        handler_result['session'] = session
        return handler_result

    return inner


def put_router_in_view_result(handler: Callable) -> Callable:
    """ Put in handler result app routes """
    @wraps(handler)
    async def inner(request: aiohttp.web.Request, *args, **kwargs) -> dict:
        """ Get routes (mapping, keys - route_name, values - urls) and put it in handler result data """
        router: Mapping = request.app.router
        handler_result: dict = await handler(request)
        # put routes data in handler result
        handler_result['router'] = router
        return handler_result

    return inner
