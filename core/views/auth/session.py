"""
Contains functions (and decorators) that control work with user data in session.

Session structure:
    session = {
        'user': {
            # db data
            'id'            : int
            'login'         : str
            'is_admin'      : int(0,1)
            'is_moderator'  : int(0,1)
            # created on authorization
            'group'         : Type[user_groups.UserGroup]
        }
        ...
    }

.. decorator:: def user_group_access_required(handler: Callable = None, *args, user_group: Type[user_groups.UserGroup]
        ) -> Callable
    Verify user group

.. function:: get_alert_message_from_session(
        request: Optional[aiohttp.web.Request], session: Optional[aiohttp_session.Session] = None ) -> str
    Return session alert message
.. function:: put_alert_message_in_session(
        request: aiohttp.web.Request, alert_message: str, session: aiohttp_session.Session = None) -> None
    Put alert message in the session
"""

from functools import wraps
from typing import (
    Callable,
    Optional,
    Type,
    Union
)

import aiohttp.web
import aiohttp_session

from . import user_groups
from .. import (
    helpers,
    utils
)


def user_group_access_required(handler: Callable = None, *args, user_group: Type[user_groups.UserGroup]) -> Callable:
    """
    Verify user access by given user group.

    :param handler: view function
    :type handler: Callable
    :param user_group: user group
    :type user_group: Type[user_groups.UserGroup]

    :return: inner function
    :rtype: Callable
    """

    if handler is None:
        return lambda handler: user_group_access_required(
            handler=handler,
            user_group=user_group
        )

    @wraps(handler)
    @utils.view_decorator
    async def inner(handler_argument: Union[aiohttp.web.View, aiohttp.web.Request], request: aiohttp.web.Request
                    ) -> Union[dict, aiohttp.web.HTTPFound]:
        """
        Verify user access group.

        :param handler_argument: argument that will be passed in view handler
        :type handler_argument: Union[aiohttp.web.View, aiohttp.web.Request]
        :param request: request
        :type request: aiohttp.web.Request

        :return: handler result or redirect
        :rtype: Union[dict, aiohttp.web.HTTPFound]

        :raises aiohttp.web.HTTPUnauthorized: HTTP 401 raised if user unauthorized
        :raises aiohttp.web.HTTPUnauthorized: HTTP 401 raised if user unauthorized
        """

        session = await aiohttp_session.get_session(request)
        session_user_group = session.get('user', {}).get('group')

        if user_group == user_groups.Visitor:
            if user_group is not None:
                return helpers.redirect_by_route_name(request, 'index')
        else:
            if session_user_group is None:
                raise aiohttp.web.HTTPUnauthorized
            else:
                if issubclass(session_user_group, user_group):
                    handler_result = await handler(handler_argument)

                    return handler_result
                else:
                    raise aiohttp.web.HTTPForbidden

    return inner


async def get_alert_message_from_session(request: Optional[aiohttp.web.Request],
                                         session: Optional[aiohttp_session.Session] = None
                                         ) -> str:
    """
    Return alert message that in the session.

    If it is possibility to pass directly session - invoke function like:
    await get_alert_message_from_session(request=None, session=session_obj)

    :param request: request (to get session)
    :type request: Optional[aiohttp.web.Request]
    :param session: session (if it is possibility to pass directly session - without request)
    :type session: aiohttp_session.Session

    :return: alert message
    :rtype: str
    """

    session = session if session is not None else await aiohttp_session.get_session(request)

    alert_message = ''
    if 'message' in session:
        alert_message = session.pop('message')

    return alert_message


async def put_alert_message_in_session(request: aiohttp.web.Request,
                                       alert_message: str,
                                       session: aiohttp_session.Session = None
                                       ) -> None:
    """
    Put alert message in the session.

    If it is possibility to pass directly session - invoke function like:
    await put_alert_message_in_session(request=None, alert_message=message, session=session_obj)

    :param request: request (to get session)
    :type request: aiohttp.web.Request
    :param alert_message: message that will be saved in the session
    :type alert_message: str
    :param session: session (if it is possibility to pass directly session - without request)
    :type session: aiohttp_session.Session

    :return: None
    :rtype: None
    """

    session = session if session else await aiohttp_session.get_session(request)

    session['message'] = alert_message
