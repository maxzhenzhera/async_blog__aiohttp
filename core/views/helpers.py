"""
Contains functions that help handle and finalize view result.

.. decorator:: put_session_data_in_view_result(handler: Callable = None, *args, put_alert_message: bool = False
        ) -> Callable:
    Put in handler result additional data (session data, alert message)

.. function:: redirect_by_url(url: Union[str, yarl.URL], *args, is_safe: bool = False
        ) -> Union[aiohttp.web.HTTPFound, aiohttp.web.HTTPSeeOther]
    Redirect by url
.. function:: redirect_by_route_name(request: aiohttp.web.Request, route_name: str, *args, is_safe: bool = False,
        **kwargs: Any) -> Union[aiohttp.web.HTTPFound, aiohttp.web.HTTPSeeOther]
    Redirect by route name
.. function:: redirect_back_to_the_form_with_alert_message_in_session(request: aiohttp.web.Request,
        error: Union[pydantic.ValidationError, Exception, str], *args, redirect_url: Union[str, yarl.URL] = None,
        redirect_route_name: str = None, **kwargs: Any) -> aiohttp.web.HTTPFound
    Redirect on the page by passed param with alert message in the session
.. function:: get_id_param_from_url(request: aiohttp.web.Request) -> int
    Return id param from url
.. function:: get_id_param_from_form_data(data: multidict.MultiDictProxy) -> int
    Return id param from form data
.. function:: get_user_id_from_session(request: aiohttp.web.Request) -> int
    Return uer id param from session
.. function:: save_user_image(filepath: pathlib.Path, image_field: aiohttp.multipart.BodyPartReader) -> None
    Save user image
.. function:: delete_user_image(filepath: pathlib.Path) -> None
    Delete user image
"""

from functools import wraps
import pathlib
from typing import (
    Any,
    Callable,
    Union
)

import aiohttp.web
import aiohttp_session
import multidict
import pydantic
import yarl

from . import (
    auth,
    utils
)
from ..database import validators


def put_session_data_in_view_result(handler: Callable = None, *args, put_alert_message: bool = False) -> Callable:
    """
    Put in handler result session data.

    :param handler: view function
    :type handler: Callable
    :keyword put_alert_message: with this flag alert message will be removed from session (will be shown only once)
    :type put_alert_message: bool

    :return: inner function
    :rtype: Callable
    """

    if handler is None:
        return lambda handler: put_session_data_in_view_result(handler, put_alert_message=put_alert_message)

    @wraps(handler)
    @utils.view_decorator
    async def inner(handler_argument: Union[aiohttp.web.View, aiohttp.web.Request], request: aiohttp.web.Request
                    ) -> dict:
        """
        Get session data and put it in handler result.

        :param handler_argument: argument that will be passed in view handler
        :type handler_argument: Union[aiohttp.web.View, aiohttp.web.Request]
        :param request: request (to get additional data (router, session))
        :type request: aiohttp.web.Request

        :return: handler result with session data
        :rtype: dict
        """

        handler_result: dict = await handler(handler_argument)

        session = await aiohttp_session.get_session(request)

        if put_alert_message:
            alert_message = await auth.session.get_alert_message_from_session(None, session)
            handler_result['message'] = alert_message

        handler_result['session'] = session

        return handler_result

    return inner


def redirect_by_url(url: Union[str, yarl.URL], *args, is_safe: bool = False
                    ) -> Union[aiohttp.web.HTTPFound, aiohttp.web.HTTPSeeOther]:
    """
    Return redirect object by url.

    :param url: url for redirection
    :type url: Union[str, yarl.URL]
    :keyword is_safe: the redirected location will be retrieved with GET (safe after a POST)
    :type is_safe: bool

    :return: redirect object
    :rtype: Union[aiohttp.web.HTTPFound, aiohttp.web.HTTPSeeOther]
    """

    redirect_obj = aiohttp.web.HTTPSeeOther(url) if is_safe else aiohttp.web.HTTPFound(url)

    return redirect_obj


def redirect_by_route_name(request: aiohttp.web.Request, route_name: str, *args, is_safe: bool = False, **kwargs: Any
                           ) -> Union[aiohttp.web.HTTPFound, aiohttp.web.HTTPSeeOther]:
    """
    Return redirect object by route name.

    :param request: request
    :type request: aiohttp.web.Request
    :param route_name: route name
    :type route_name: str
    :keyword is_safe: the redirected location will be retrieved with GET (safe after a POST)
    :type is_safe: bool
    :keyword kwargs: named argument that will be passed in url
    :type kwargs: Any

    :return: redirect object
    :rtype: Union[aiohttp.web.HTTPFound, aiohttp.web.HTTPSeeOther]
    """

    url_params = {key: str(value) for key, value in kwargs.items()}

    url = request.app.router[route_name].url_for(**url_params)
    redirect_obj = aiohttp.web.HTTPSeeOther(url) if is_safe else aiohttp.web.HTTPFound(url)

    return redirect_obj


async def redirect_back_to_the_form_with_alert_message_in_session(request: aiohttp.web.Request,
                                                                  error: Union[
                                                                      pydantic.ValidationError, Exception, str
                                                                  ],
                                                                  *args,
                                                                  redirect_url: Union[str, yarl.URL] = None,
                                                                  redirect_route_name: str = None,
                                                                  **kwargs: Any
                                                                  ) -> aiohttp.web.HTTPFound:
    """
    Parse error, put in session and then redirect back to form.
    It is mandatory to pass on of the keyword arguments: redirect location by url or by route name.

    If 2 redirect location arguments were passed - will redirect by first argument by order - `redirect_url`

    :param request: request
    :type request: aiohttp.web.Request
    :param error: error that raised during validation
    :type error: Union[pydantic.ValidationError, Exception, str]
    :keyword redirect_url: url
    :type redirect_url: Union[str, yarl.URL]
    :keyword redirect_route_name: route name
    :type redirect_route_name: str
    :keyword kwargs: named argument that will be passed in url (by route name)
    :type kwargs: Any

    :return: redirect object
    :rtype: aiohttp.web.HTTPFound
    """

    if redirect_url:
        redirect = redirect_by_url(redirect_url)
    elif redirect_route_name:
        redirect = redirect_by_route_name(request, redirect_route_name, **kwargs)
    else:
        message = '`redirect_back_to_the_form_with_alert_message_in_session` expected 1 mandatory keyword argument, '
        message += 'got 0'
        raise TypeError(message)

    if isinstance(error, pydantic.ValidationError):
        alert_message = validators.get_formatted_error_message(error)
    else:
        alert_message = str(error)

    await auth.session.put_alert_message_in_session(request, alert_message)

    return redirect


def get_id_param_from_url(request: aiohttp.web.Request) -> int:
    """
    Return id param from url.
    It is might be used instead: `request.match_info['id']`.

    :param request: request
    :type request: aiohttp.web.Request

    :return: id
    :rtype: int
    """

    id_ = int(request.match_info['id'])

    return id_


def get_id_param_from_form_data(data: multidict.MultiDictProxy) -> int:
    """
    Return entity id from form data.
    It is might be used instead: `int(data['id')`.

    :param data: form data
    :type data: multidict.MultiDictProxy

    :return: id
    :rtype: int

    :raises aiohttp.web.HTTPBadRequest: raised if the form data do not have expected params
    """

    try:
        id_ = int(data['id'])
    except KeyError:
        raise aiohttp.web.HTTPBadRequest(reason='the form data do not have expected params')
    else:
        return id_


async def get_user_id_from_session(request: aiohttp.web.Request) -> int:
    """
    Return user-id from session.

    :param request: request
    :type request: aiohttp.web.Request

    :return: user-id
    :rtype: int
    """

    session = await aiohttp_session.get_session(request)
    user_id = session['user']['id']

    return user_id


async def save_user_image(filepath: pathlib.Path, image_field: aiohttp.multipart.BodyPartReader) -> None:
    """
    Save user image.

    :param filepath: absolute path of the image
    :type filepath: pathlib.Path
    :param image_field: image field (got from mupltipart reader)
    :type image_field: aiohttp.multipart.BodyPartReader

    :return: None
    :rtype: None
    """

    with open(filepath, 'wb') as file:
        while True:
            chunk = await image_field.read_chunk()

            if not chunk:
                break

            file.write(chunk)


async def delete_user_image(filepath: pathlib.Path) -> None:
    """
    Delete user image.

    :param filepath: absolute path of the image
    :type filepath: pathlib.Path

    :return: None
    :rtype: None
    """

    filepath.unlink(missing_ok=True)
