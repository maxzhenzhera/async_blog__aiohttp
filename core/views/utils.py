"""
Auxiliary functions and decorators.

.. decorator:: view_decorator(inner_decorator_function: Callable) -> Callable:
    Envelopes inner decorator function, support different types of views (functions, class-based).
"""

from functools import wraps
from typing import (
    Any,
    Callable,
    Union
)

import aiohttp.web


def view_decorator(inner_decorator_function: Callable) -> Callable:
    """
    Envelopes inner decorator function and pass in 2 objects:
    initial view argument (aiohttp.web.Request or aiohttp.web.View) and request (aiohttp.web.Request).

    Decorator used in other view decorators.
    So, support different types of views (functions, class-based).

    Enveloped function must get params like:
    function_name(handler_argument, request)

    :param inner_decorator_function: enveloped inner decorator function
    :type inner_decorator_function: Callable

    :return: inner function
    :rtype: Callable
    """

    @wraps(inner_decorator_function)
    async def inner(handler_argument: Union[aiohttp.web.Request, aiohttp.web.View]) -> Any:
        """
        Invoke inner decorator function with 2 arguments:
        `handler_argument` - initial handler argument and `request` - request that gotten from `handler_argument`.

        :param handler_argument: initial handler argument - obj that view handler get
        :type handler_argument: Union[aiohttp.web.Request, aiohttp.web.View]

        :return: inner decorator function result
        :rtype: Any

        :raises ValueError: might be raised if not view function was enveloped (unexpected type of argument)
        """

        if isinstance(handler_argument, aiohttp.web.Request):
            request = handler_argument
        elif isinstance(handler_argument, aiohttp.web.View):
            request = handler_argument.request
        else:
            message = 'Unexpected type of the function (method) argument. '
            message += 'Expected ( obj: Union[aiohttp.web.Request, aiohttp.web.View] ). '
            message += f'Given (obj: {type(handler_argument)}). '
            message += 'Decorator must envelop only view functions (or methods if view is class based).'
            raise ValueError(message)

        inner_decorator_function_result = await inner_decorator_function(
            handler_argument=handler_argument,
            request=request
        )

        return inner_decorator_function_result

    return inner
