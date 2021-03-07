"""
Auxiliary functions and decorators.

.. decorator:: view_decorator(inner_decorator_function: Callable) -> Callable:
    Envelopes inner decorator function, support different types of views (functions, class-based)
.. decorator:: handle_local_error(function: Callable = None, *args,
        except_error: Union[Type[Exception], tuple[Type[Exception]]], raise_error: Type[Exception]  ) -> Callable
    Envelopes any async function and handle particular error
"""

from functools import wraps
from typing import (
    Any,
    Callable,
    Type,
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

    :raises [in inner] ValueError: might be raised if not view function was enveloped (unexpected type of argument)
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


def handle_local_error(function: Callable = None, *args,
                       except_error: Union[Type[Exception], tuple[Type[Exception]]], raise_error: Type[Exception]
                       ) -> Callable:
    """
    Envelopes any function and handle local error (that might be raised during function work).
    It is compulsory to pass:
        - as `except_error` - error type(s), that will be handled,
        - as `raise_error` - error type, that will be raised [if `except_error` was handled].

    'Errors should never pass silently.' - so, decorator always re-raises error if one was handled.

    So, the main goal of the decorator - re-raise particular error for global handling in middlewares.

    :param function: some async function
    :type function: Callable

    :keyword except_error: error type, that will be handled (might be passed tuple of Exception-s)
    :type except_error: Union[Type[Exception], tuple[Type[Exception]]]
    :keyword raise_error: error type, that will be raised [if `except_error` was handled]
    :type raise_error: Type[Exception]

    :return: function result
    :rtype: Any

    :raises [in inner] `raise_error`: raised if the `except_error` was handled
    """

    if function is None:
        return lambda function: handle_local_error(function, except_error=except_error, raise_error=raise_error)

    async def inner(*args, **kwargs) -> Any:
        """
        Handle function work [and re-raise error if expected error was caught].

        :return: function result
        :rtype: Any

        :raises `raise_error`: raised if the `except_error` was handled
        """

        try:
            function_result = await function(*args, **kwargs)
        except except_error as caught_error:
            raise raise_error from caught_error
        else:
            return function_result

    return inner
