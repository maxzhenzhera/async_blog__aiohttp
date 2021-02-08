"""
Contains functions that help in work with sessions.

Session structure:
    session = {
        'user': {
            'id'            : int
            'login'         : str
            'is_admin'      : literal-bool[int(0,1)]
            'is_moderator'  : literal-bool[int(0,1)]
        }
        ...
    }

Hierarchy of grants:
- `admin`           (control (create and delete) moderators;    + `moderator` rights)
    - `moderator`   (control (delete) users' posts;             + `user` rights)
        - `user`    (control self posts (create, update, delete), ability to control notes (personal marks))
- `visitor`         (not like a grant, but like the type of grants hierarchy, unauthorized, ability to read posts)


Functions {decorators}:
    def login_required(handler: Callable = None, *args, grant: str = 'user', **kwargs) -> Callable:
    = check requirement (grant, authorization) in session
    --------------------------------------------------------------------------------------------------------------------
"""

from functools import wraps
from typing import (
    Callable
)

import aiohttp.web
import aiohttp_session


def login_required(handler: Callable = None, *args, grant: str = 'user', **kwargs) -> Callable:
    """
    Verify user authorization and / or user grant (`admin`, `,moderator`) if indicated.

    Keyword `grant`:
        type: str
        possible arguments:         (what do)                       (condition of success)
            - 'user'        - check user authorization      - session has `user` data
            - 'moderator'   - check user `moderator` grant  - a column `is_moderator` or `is_admin` in `user` is True
            - 'admin'       - check user `admin` grant      - the column `is_admin` in `user` is True
        default: 'user'

        if argument is not str type                     - TypeError raised,
        if argument is not in possible arguments list   - ValueError raised.

    Return handler result.

    Raises:
         TypeError                              - if keyword argument `grant` is not str type
         ValueError                             - if keyword argument `grant` is not in possible arguments list
         aiohttp.web.HTTPUnauthorized (401)     - if user is not authorized
         aiohttp.web.HTTPForbidden (403)        - if user does not have grant
    """

    if handler is None:
        return lambda func: login_required(handler=func, grant=grant)

    @wraps(handler)
    async def inner(request: aiohttp.web.Request, *args, **kwargs) -> dict:
        """ Get user data from session and check requirements (grants) """
        session = await aiohttp_session.get_session(request)
        if 'user' in session:
            if grant == 'user':
                # verified
                pass
            elif grant == 'moderator':
                if not (session['user']['is_moderator'] or session['user']['is_admin']):
                    raise aiohttp.web.HTTPForbidden
            elif grant == 'admin':
                if not session['user']['is_admin']:
                    raise aiohttp.web.HTTPForbidden
            else:
                if isinstance(grant, str):
                    message = 'Keyword argument `grant` may have only value that in possible arguments list. '
                    message += 'Check the function doc string!'
                    raise ValueError(message)
                else:
                    message = f'Keyword argument `grant` might be only str type. Not {type(grant)}'
                    raise TypeError(message)

            handler_result = await handler(request)
            return handler_result
        else:
            raise aiohttp.web.HTTPUnauthorized

    return inner
