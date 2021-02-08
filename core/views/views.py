"""
Contains view-functions that return html page by particular url-route.


Functions:
        ...
    --------------------------------------------------------------------------------------------------------------------
"""


import aiohttp.web
import aiohttp_session
import aiohttp_jinja2

from core.database import db
from core.views import (
    auth,
    pagination,
    session,
    validators,
    views_decorators
)


# # ------------------------- MAIN PARTITION


@aiohttp_jinja2.template('index.html')
@views_decorators.put_session_data_in_view_result
@views_decorators.put_router_in_view_result
async def index(request: aiohttp.web.Request) -> dict:
    """ View for '/' url """
    return {}


@aiohttp_jinja2.template('contacts.html')
@views_decorators.put_session_data_in_view_result
@views_decorators.put_router_in_view_result
async def contacts(request: aiohttp.web.Request) -> dict:
    """ View for '/contacts/' url """
    return {}


#
# posts partition
#


@aiohttp_jinja2.template('posts.html')
@views_decorators.put_session_data_in_view_result
@views_decorators.put_router_in_view_result
async def posts(request: aiohttp.web.Request) -> dict:
    """ View for '/posts/' url with possible parameters (page: int, rubric: int, quantity: int, keyword: str) """
    url_params = request.rel_url.query
    validated_params = validators.ParamsHandler(url_params, validators.UrlParams).validated_params

    async with request.app['db'].acquire() as connection:
        posts_data = await db.fetch_all_posts(connection, **validated_params)
        pagination_data = await pagination.Pagination(connection, 'posts', **validated_params).pagination
        data = {
            'posts': posts_data,
            'pagination': pagination_data,
        }

        return data


@aiohttp_jinja2.template('post.html')
@views_decorators.put_session_data_in_view_result
@views_decorators.put_router_in_view_result
async def post(request: aiohttp.web.Request) -> dict:
    """ View for '/posts/{id}/' url """
    post_id = request.match_info['id']

    async with request.app['db'].acquire() as connection:
        post_data = await db.fetch_one_post(connection, post_id)
        data = {
            'post': post_data,
        }

        return data


@aiohttp_jinja2.template('post.html')
@views_decorators.put_session_data_in_view_result
@views_decorators.put_router_in_view_result
async def random_post(request: aiohttp.web.Request) -> dict:
    """ View for '/posts/{id}/' url """
    async with request.app['db'].acquire() as connection:
        post_data = await db.fetch_one_random_post(connection)
        data = {
            'post': post_data,
        }

        return data


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
@views_decorators.put_session_data_in_view_result
@views_decorators.put_router_in_view_result
async def post_rubrics(request: aiohttp.web.Request) -> dict:
    """ View for '/posts/rubrics/' url """
    async with request.app['db'].acquire() as connection:
        rubrics = await db.fetch_all_post_rubrics(connection)
        data = {
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
#
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


# @aiohttp_jinja2.template('post_rubrics.html')
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
    # @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/notes/rubrics/create/' url {GET} """
        return {}

    async def post(self):
        """ View for '/notes/rubrics/create/' url {POST} """
        return {}


class NoteRubricEditing(aiohttp.web.View):
    """ View class for '/notes/rubrics/{id}/edit/' url. Implement GET and POST requests. """
    # @aiohttp_jinja2.template('post_creation_form.html')
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
    @aiohttp_jinja2.template('sign_in.html')
    @views_decorators.put_session_data_in_view_result
    @views_decorators.put_router_in_view_result
    async def get(self) -> dict:
        """ View for '/user/register/' url {GET} """

        return {}

    # Handlers should be coroutines accepting self only and returning response object as regular web-handler.
    # Request object can be retrieved by View.request property.

    async def post(self):
        """ View for '/user/register/' url {POST} """
        return {}


class UserAuthorization(aiohttp.web.View):
    """ View class for '/user/login/ url. Implement GET and POST requests. """
    # @aiohttp_jinja2.template('post_creation_form.html')
    async def get(self) -> dict:
        """ View for '/user/login/' url {GET} """
        return {}

    async def post(self):
        """ View for '/user/login/' url {POST} """
        return {}


class UserSettingsEditing(aiohttp.web.View):
    """ View class for '/user/settings/edit/ url. Implement GET and POST requests. """
    # @aiohttp_jinja2.template('post_creation_form.html')
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
