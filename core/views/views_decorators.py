"""
Contains functions that help handle and finalize view result


Functions {decorators}:
    def put_request_in_decorator_inner_function(inner_decorator_function: Callable) -> Callable:
    = pass request object in the view decorators
    --------------------------------------------------------------------------------------------------------------------
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
    Callable,
    Type,
    Union
)

import aiohttp.web
import aiohttp_session


def put_request_in_decorator_inner_function(inner_decorator_function: Callable) -> Callable:
    """
    Put request object in the inner decorator function.

    Views might be made like functions or on class base.
    If handler is function:
        decorator inner function gets as argument request: aiohttp.web.Request;
    elif handler is class (with implemented methods [get, post, ...]):
        decorator inner function gets as argument the instance of view class,
        instance: aiohttp.web.View.

    Since views decorators get as main argument from view request: aiohttp.web.Request,
    that decorator help with the correct distribution of argument.

    So, if decorated view is function:
            pass in decorator inner function request;
        elif decorated view is method in view class:
            pass in decorator inner function property `request` of the class view instance.
    """

    @wraps(inner_decorator_function)
    async def inner(obj: Union[aiohttp.web.Request, Type[aiohttp.web.View]], *args, **kwargs):
        """ Pass request object in decorator inner function """
        if isinstance(obj, aiohttp.web.Request):
            return await inner_decorator_function(obj, *args, **kwargs)
        elif isinstance(obj, aiohttp.web.View):
            return await inner_decorator_function(obj.request, *args, **kwargs)
        else:
            message = 'It`s impossible! I catch request from view, here may be only 2 type of arguments!'
            raise ValueError(message)

    return inner


def put_session_data_in_view_result(handler: Callable) -> Callable:
    """ Put in handler result session data """
    @wraps(handler)
    @put_request_in_decorator_inner_function
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
    @put_request_in_decorator_inner_function
    async def inner(request: aiohttp.web.Request, *args, **kwargs) -> dict:
        """ Get routes (mapping, keys - route_name, values - urls) and put it in handler result data """
        router: Mapping = request.app.router
        handler_result: dict = await handler(request)
        # put routes data in handler result
        handler_result['router'] = router
        return handler_result

    return inner
