"""
Contains view-functions that return html page by particular url-route.


Functions:
        ...
    --------------------------------------------------------------------------------------------------------------------
"""

from collections.abc import Callable
from functools import wraps
from typing import (
    Any,
    Union
)

import aiohttp.web
import aiohttp_session
import aiohttp_jinja2
from loguru import logger

from core import db
from core import utils


# ------------------------- HELP FUNCTIONS AND DECORATORS


def put_session_data_in_view_result(handler: Callable) -> Callable:
    """ Put in view result session data """
    @wraps(handler)
    async def inner(request: aiohttp.web.Request, *args, **kwargs) -> dict:
        """ Get session by request and put in handler result data """
        session = await aiohttp_session.get_session(request)
        handler_result: dict = await handler(request)
        # put session data in handler result
        handler_result['session'] = session
        # return handler result with session data
        return handler_result

    return inner


def login_required(handler: Callable = None, *args, return_type: str = 'handler_result') -> Callable:
    """
    Verify user authorization.

    Keyword argument `return_type` may be:
    - 'handler_result'      (default)   -> result of handler function
    - 'handler_function'                -> object of the handler function

    Raise `aiohttp.web.HTTPUnauthorized` (401) if user is not authorized.
    """

    # if in decorator was passed keyword argument -> function argument (`handler`) stayed with default value - None
    if handler is None:
        # get function by lambda argument and then in lambda body invoke decorator again
        # with keyword argument (was passed in the start) and function argument (was passed in lambda statement)
        return lambda func: login_required(handler=func, return_type=return_type)

    @wraps(handler)
    async def inner(request: aiohttp.web.Request, *args, **kwargs) -> Union[Callable, Any]:
        """ Get user authorization data from session to pass next step if exist - else raise an error (HTTP - 401) """
        session = await aiohttp_session.get_session(request)
        if 'user' in session:
            # verified - passed to next step
            # ...
            # return the result based on the keyword argument (`return_type`)
            if return_type == 'handler_result':
                handler_result = await handler(request)
                return handler_result
            elif return_type == 'handler_function':
                handler_function = handler
                return handler_function
            else:
                if isinstance(return_type, str):
                    error_message = "Correct argument option('handler_result', 'handler_function') expected. "
                    error_message += f"Instead got {return_type}."
                    raise ValueError(error_message)
                else:
                    error_message = "Keyword `return_type` must be a `str` type. "
                    error_message += f"Instead got type `{type(return_type)}`."
                    raise TypeError(error_message)
        else:
            raise aiohttp.web.HTTPUnauthorized

    return inner


def grant_required(handler: Callable, *args, grant_type: str = 'moderator', return_type: str = ''):
    """ Verify user admin grant """


# ------------------------- HELP FUNCTIONS AND DECORATORS


# # ------------------------- MAIN PARTITION


@aiohttp_jinja2.template('index.html')
async def index(request: aiohttp.web.Request) -> dict:
    """ View for '/' url """
    session = await aiohttp_session.get_session(request)
    data = {
        'session': session
    }
    return data


@aiohttp_jinja2.template('contacts.html')
async def contacts(request: aiohttp.web.Request) -> dict:
    """ View for '/contacts/' url """
    session = await aiohttp_session.get_session(request)
    print(session)
    data = {
        'session': None
    }
    return data


#
# posts partition
#


@aiohttp_jinja2.template('posts.html')
async def posts(request: aiohttp.web.Request) -> dict:
    """ View for '/posts/' url with possible parameters (page: int, rubric: int, quantity: int, keyword: str) """
    url_params_for_checking = [
        utils.UrlParam('rubric', int, 'rubric_id'),
        utils.UrlParam('page', int),
        utils.UrlParam('quantity', int, 'rows_quantity'),
        utils.UrlParam('keyword', str)
    ]
    parameters = utils.UrlParamsHandler(request, url_params_for_checking).params
    async with request.app['db'].acquire() as connection:
        if 'rubric_id' in parameters:
            posts_ = await db.fetch_all_posts_by_rubric_for_page(connection, **parameters)
        elif 'keyword' in parameters:
            posts_ = await db.fetch_all_posts_by_keyword(connection, **parameters)
        else:
            posts_ = await db.fetch_all_posts_for_page(connection, **parameters)

        possible_pages_quantity = await db.fetch_possible_pages_quantity(connection, **parameters)
        data = {
            'session': None,
            'posts': posts_,
            'possible_pages_quantity': possible_pages_quantity,
            'page': parameters['page'] if 'page' in parameters else 1
        }
        return data


@aiohttp_jinja2.template('post.html')
async def post(request: aiohttp.web.Request) -> dict:
    """ View for '/posts/{id}/' url """
    return {}


class PostCreation(aiohttp.web.View):
    """ View class for '/posts/create/' url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/posts/create/' url {GET} """
        return {}

    # post - the request type, not object like article
    async def post(self):
        """ View for '/posts/create/' url {POST} """
        return {}


class PostEditing(aiohttp.web.View):
    """ View class for '/posts/{id}/edit/' url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/posts/{id}/edit/' url {GET} """
        return {}

    # post - the request type, not object like article
    async def post(self):
        """ View for '/posts/{id}/edit/' url {POST} """
        return {}


@aiohttp_jinja2.template('post_rubrics.html')
async def post_rubrics(request: aiohttp.web.Request) -> dict:
    """ View for '/posts/rubrics/' url """
    async with request.app['db'].acquire() as connection:
        rubrics = await db.fetch_all_post_rubrics(connection)
        data = {
            'session': None,
            'rubrics': rubrics
        }
        return data


class PostRubricCreation(aiohttp.web.View):
    """ View class for '/posts/rubrics/create/' url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/posts/rubrics/create/' url {GET} """
        return {}

    async def post(self):
        """ View for '/posts/rubrics/create/' url {POST} """
        return {}


class PostRubricEditing(aiohttp.web.View):
    """ View class for '/posts/rubrics/{id}/edit/' url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/posts/rubrics/{id}/edit/' url {GET} """
        return {}

    async def post(self):
        """ View for '/posts/rubrics/{id}/edit/' url {POST} """
        return {}


#
# notes partition
#


@aiohttp_jinja2.template('posts.html')
async def notes(request: aiohttp.web.Request) -> dict:
    """ View for '/notes/' url """
    return {}


@aiohttp_jinja2.template('post.html')
async def note(request: aiohttp.web.Request) -> dict:
    """ View for 'notes/{id}/' url """
    return {}


class NoteCreation(aiohttp.web.View):
    """ View class for '/notes/create/' url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/notes/create/' url {GET} """
        return {}

    async def post(self):
        """ View for '/notes/create/' url {POST} """
        return {}


class NoteEditing(aiohttp.web.View):
    """ View class for '/notes/{id}/edit/' url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/notes/{id}/edit/' url {POST} """
        return {}

    async def post(self):
        """ View for '/notes/{id}/edit/' url {GET} """
        return {}


@aiohttp_jinja2.template('post_rubrics.html')
async def note_rubrics(request: aiohttp.web.Request) -> dict:
    """ View for '/notes/rubrics/' url """
    async with request.app['db'].acquire() as connection:
        rubrics = await db.fetch_all_post_rubrics(connection)
        data = {
            'session': None,
            'rubrics': rubrics
        }
        return data


class NoteRubricCreation(aiohttp.web.View):
    """ View class for '/notes/rubrics/create/' url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/notes/rubrics/create/' url {GET} """
        return {}

    async def post(self):
        """ View for '/notes/rubrics/create/' url {POST} """
        return {}


class NoteRubricEditing(aiohttp.web.View):
    """ View class for '/notes/rubrics/{id}/edit/' url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/notes/rubrics/{id}/edit/' url {GET} """
        return {}

    async def post(self):
        """ View for '/notes/rubrics/{id}/edit/' url {POST} """
        return {}


#
# user partition
#


class UserRegistration(aiohttp.web.View):
    """ View class for '/user/register/ url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/user/register/' url {GET} """
        return {}

    async def post(self):
        """ View for '/user/register/' url {POST} """
        return {}


class UserAuthorization(aiohttp.web.View):
    """ View class for '/user/login/ url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/user/login/' url {GET} """
        return {}

    async def post(self):
        """ View for '/user/login/' url {POST} """
        return {}


class UserSettingsEditing(aiohttp.web.View):
    """ View class for '/user/settings/edit/ url. Implement GET and POST requests. """
    @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/user/settings/edit/' url {GET} """
        return {}

    async def post(self):
        """ View for '/user/settings/edit/' url {POST} """
        return {}


async def user_logout(request: aiohttp.web.Request) -> dict:
    """ View for '/user/logout/' url """
    return {}


#
# posts < --- > user partition
#


async def user_posts(request: aiohttp.web.Request) -> dict:
    """ View for '/my/posts/' url """
    return {}
