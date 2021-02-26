"""
Contains view-functions that return html page by particular url-route.


Functions:
        ...
    --------------------------------------------------------------------------------------------------------------------
"""

from typing import Union

import aiohttp.web
import aiohttp_jinja2
import aiohttp_session
import pydantic

from . import (
    auth,
    pagination,
    helpers
)
from ..database import db, validators


# main partition


class Index(aiohttp.web.View):
    """ View for '/' url """

    @aiohttp_jinja2.template('index.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """ Return index page """
        return {}


class Contacts(aiohttp.web.View):
    """ View for '/contacts/' url """

    @aiohttp_jinja2.template('contacts.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """ Return contacts page """
        return {}


# posts partition

# # posts

class Posts(aiohttp.web.View):
    """ View for '/posts/' url """

    @aiohttp_jinja2.template('posts.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """
        Return page with posts.

        Possible url parameters:
            page: int       - page number
            rubric: int     - rubric id
            quantity: int   - posts quantity
            keyword: str    - search word
        """

        url_params = self.request.rel_url.query
        validated_url_params = validators.PostUrlParams(**url_params)

        async with self.request.app['db'].acquire() as connection:
            posts_data = await db.fetch_all_posts(connection, validated_url_params)
            possible_pages_quantity = await db.fetch_posts_possible_pages_quantity(connection, validated_url_params)

        pagination_data = pagination.Pagination(possible_pages_quantity, validated_url_params.page).pagination_data

        data = {
            'posts': posts_data,
            'pagination': pagination_data,
        }

        return data


class Post(aiohttp.web.View):
    """ View for '/posts/<id: int>/ url """

    @aiohttp_jinja2.template('post.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """ Return page with 1 particular post """
        post_id = helpers.get_id_param_from_url(self.request)

        async with self.request.app['db'].acquire() as connection:
            post_data = await db.fetch_one_post(connection, post_id)

        data = {
            'post': post_data,
        }

        return data


class RandomPost(aiohttp.web.View):
    """ View for '/posts/random/' url """

    @aiohttp_jinja2.template('post.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """ Return page with random post """
        async with self.request.app['db'].acquire() as connection:
            post_data = await db.fetch_one_random_post(connection)

        data = {
            'post': post_data,
        }

        return data


class PostCreation(aiohttp.web.View):
    """ View for '/posts/create/' url """

    @aiohttp_jinja2.template('post_creation.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with post creation form """
        async with self.request.app['db'].acquire() as connection:
            post_rubrics = await db.fetch_all_post_rubrics(connection)

        data = {
            'rubrics': post_rubrics
        }

        return data

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Handle post creation form """
        data = await self.request.post()

        session = await aiohttp_session.get_session(self.request)
        user_id = session['user']['id']

        try:
            post = validators.PostCreation(user_id=user_id, **data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='posts-create'
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.insert_post(connection, post)

            return helpers.redirect_by_route_name(self.request, 'user-posts')


class PostEditingForm(aiohttp.web.View):
    """ View for '/posts/<id: int>/edit/' url """

    @aiohttp_jinja2.template('post_editing.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return filled post form for editing  """
        post_id = helpers.get_id_param_from_url(self.request)

        _, post = await auth.authentication_policy.authenticate_post_owner(self.request, post_id)

        async with self.request.app['db'].acquire() as connection:
            post_rubrics = await db.fetch_all_post_rubrics(connection)

        data = {
            'post': post,
            'rubrics': post_rubrics
        }

        return data


class PostEditing(aiohttp.web.View):
    """ View for '/posts/edit/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Handle post editing form """
        data = await self.request.post()

        post_id = helpers.get_id_param_from_form_data(data)

        await auth.authentication_policy.authenticate_post_owner(self.request, post_id)

        try:
            post = validators.PostEditing(**data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='posts-id-edit', id=post_id
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.update_post(connection, post_id, post)

            return helpers.redirect_by_route_name(self.request, 'posts-id', id=post_id)


class PostDeleting(aiohttp.web.View):
    """ View for '/posts/delete/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Delete particular post """
        data = await self.request.post()

        post_id = helpers.get_id_param_from_form_data(data)

        await auth.authentication_policy.authenticate_post_owner(self.request, post_id)

        async with self.request.app['db'].acquire() as connection:
            await db.delete_post(connection, post_id)

        return helpers.redirect_by_route_name(self.request, 'user-posts')


# # post rubrics


class PostRubrics(aiohttp.web.View):
    """ View for '/posts/rubrics/' url """

    @aiohttp_jinja2.template('post_rubrics.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """ Return page with list of post rubrics """
        async with self.request.app['db'].acquire() as connection:
            rubrics = await db.fetch_all_post_rubrics(connection)

        data = {
            'rubrics': rubrics
        }

        return data


class PostRubricCreation(aiohttp.web.View):
    """ View for '/posts/rubrics/create/' url """

    @aiohttp_jinja2.template('post_rubric_creation.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def get(self) -> dict:
        """ Return page with post rubric creation form """
        return {}

    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def post(self):
        """ View for '/posts/rubrics/create/' url {POST} """
        data = await self.request.post()

        try:
            post_rubric = validators.PostRubricCreation(**data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, self.request.app.router['posts-rubrics-create'].url_for()
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.insert_post_rubric(connection, post_rubric)

            return helpers.redirect_by_route_name(self.request, 'posts-rubrics')


class PostRubricEditingForm(aiohttp.web.View):
    """ View class for '/posts/rubrics/<id: int>/edit/' url """

    @aiohttp_jinja2.template('post_rubric_editing.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def get(self) -> dict:
        """ Return page with filled post rubric editing form """
        post_rubric_id = helpers.get_id_param_from_url(self.request)

        async with self.request.app['db'].acquire() as connection:
            post_rubric = await db.fetch_one_post_rubric(connection, post_rubric_id)

        data = {
            'post_rubric': post_rubric
        }

        return data


class PostRubricEditing(aiohttp.web.View):
    """ View class for '/posts/rubrics/edit/' url"""

    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def post(self):
        """ Handle post rubric editing form """
        data = await self.request.post()

        post_rubric_id = helpers.get_id_param_from_form_data(data)

        try:
            post_rubric = validators.PostRubricEditing(**data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, self.request.app.router['posts-rubrics-create'].url_for()
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.update_post_rubric(connection, post_rubric_id, post_rubric)

            return helpers.redirect_by_route_name(self.request, 'posts-rubrics')


class PostRubricDeleting(aiohttp.web.View):
    """ View for 'posts/rubrics/delete/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def post(self):
        """ Delete particular post rubric """
        data = await self.request.post()

        post_rubric_id = helpers.get_id_param_from_form_data(data)

        async with self.request.app['db'].acquire() as connection:
            await db.delete_post_rubric(connection, post_rubric_id)

            return helpers.redirect_by_route_name(self.request, 'posts-rubrics')


# notes partition


# # notes


class Notes(aiohttp.web.View):
    """ View for 'notes' url """

    @aiohttp_jinja2.template('notes.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """
        Return page with user notes.

        Possible url parameters:
            page: int       - page number
            rubric: int     - rubric id
            quantity: int   - posts quantity
        """

        url_params = self.request.rel_url.query
        validated_url_params = validators.NoteUrlParams(**url_params)

        session = await aiohttp_session.get_session(self.request)
        user_id = session['user']['id']

        async with self.request.app['db'].acquire() as connection:
            notes = await db.fetch_all_notes(connection, user_id, validated_url_params)
            possible_pages_quantity = await db.fetch_notes_possible_pages_quantity(
                connection, validated_url_params, user_id
            )
        pagination_data = pagination.Pagination(possible_pages_quantity, validated_url_params.page).pagination_data

        data = {
            'notes': notes,
            'pagination': pagination_data,
        }

        return data


class Note(aiohttp.web.View):
    """ View for '/notes/<id: int>/' url """
    @aiohttp_jinja2.template('post.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with particular note """
        note_id = helpers.get_id_param_from_url(self.request)

        note = await auth.authentication_policy.authenticate_note_owner(self.request, note_id)

        data = {
            'note': note
        }

        return data


class NoteCreation(aiohttp.web.View):
    """ View for '/notes/create/' url """

    @aiohttp_jinja2.template('note_creation.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with note creation form """
        session = await aiohttp_session.get_session(self.request)
        user_id = session['user']['id']

        async with self.request.app['db'].acquire() as connection:
            note_rubrics = await db.fetch_all_note_rubrics(connection, user_id)

        data = {
            'rubrics': note_rubrics
        }

        return data

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Handle note creation form """
        data = await self.request.post()

        session = await aiohttp_session.get_session(self.request)
        user_id = session['user']['id']

        try:
            note = validators.NoteCreation(user_id=user_id, **data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, self.request.app.router['notes-create'].url_for()
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.insert_note(connection, note)

            return helpers.redirect_by_route_name(self.request, 'notes')


class NoteEditingForm(aiohttp.web.View):
    """ View for '/notes/<id: int>/edit/' url """

    @aiohttp_jinja2.template('post_creation_form.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ View for '/notes/{id}/edit/' url {POST} """
        note_id = helpers.get_id_param_from_url(self.request)

        note = await auth.authentication_policy.authenticate_note_owner(self.request, note_id)

        session = await aiohttp_session.get_session(self.request)
        user_id = session['user']['id']

        async with self.request.app['db'].acquire() as connection:
            note_rubrics = await db.fetch_all_note_rubrics(connection, user_id)

        data = {
            'note': note,
            'rubrics': note_rubrics
        }

        return data


class NoteEditing(aiohttp.web.View):
    """ View for '/notes/edit/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Handle note editing form """
        data = await self.request.post()

        note_id = helpers.get_id_param_from_form_data(data)

        await auth.authentication_policy.authenticate_note_owner(self.request, note_id)

        try:
            note = validators.NoteEditing(**data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='notes-id-edit', id=note_id
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.update_note(connection, note_id, note)

            return helpers.redirect_by_route_name(self.request, 'notes-id')


class NoteDeleting(aiohttp.web.View):
    """ View for '/notes/delete/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Delete particular note """
        data = await self.request.post()

        note_id = helpers.get_id_param_from_form_data(data)

        await auth.authentication_policy.authenticate_post_owner(self.request, note_id)

        async with self.request.app['db'].acquire() as connection:
            await db.delete_post(connection, note_id)

        return aiohttp.web.HTTPFound(self.request.app.router['notes'].url_for())


# # note rubrics


class NoteRubrics(aiohttp.web.View):
    """ View for '/notes/rubrics/' url """

    @aiohttp_jinja2.template('note_rubrics.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with not rubrics """
        session = await aiohttp_session.get_session(self.request)
        user_id = session['user']['id']

        async with self.request.app['db'].acquire() as connection:
            rubrics = await db.fetch_all_note_rubrics(connection, user_id)

        data = {
            'rubrics': rubrics
        }

        return data


class NoteRubricCreation(aiohttp.web.View):
    """ View for '/notes/rubrics/create/' url """

    @aiohttp_jinja2.template('note_rubric_creation.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with note rubric creation form """
        return {}

    async def post(self):
        """ Handle note rubric creation form """
        data = await self.request.post()

        session = await aiohttp_session.get_session(self.request)
        user_id = session['user']['id']

        try:
            note_rubric = validators.NoteRubricCreation(user_id=user_id, **data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='notes-rubrics-create'
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.insert_note_rubric(connection, note_rubric)

            return helpers.redirect_by_route_name(self.request, 'note-rubrics')


class NoteRubricEditingForm(aiohttp.web.View):
    """ View for '/notes/rubrics/<id: int>/edit/' url """

    @aiohttp_jinja2.template('note_rubric_editing.html')
    @helpers.put_additional_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with note rubric editing form """
        note_rubric_id = helpers.get_id_param_from_url(self.request)

        note_rubric = await auth.authentication_policy.authenticate_note_rubric_owner(self.request, note_rubric_id)

        data = {
            'note_rubric': note_rubric
        }

        return data


class NoteRubricEditing(aiohttp.web.View):
    """ View for '/notes/rubrics/edit/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Handle note rubric editing form """
        data = await self.request.post()

        note_rubric_id = helpers.get_id_param_from_form_data(data)

        await auth.authentication_policy.authenticate_note_rubric_owner(self.request, note_rubric_id)

        try:
            note_rubric = validators.NoteRubricEditing(**data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='notes-rubrics-create'
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.update_note_rubric(connection, note_rubric_id, note_rubric)

            return helpers.redirect_by_route_name(self.request, 'notes-rubrics')


class NoteRubricDeleting(aiohttp.web.View):
    """ View for '/notes/rubrics/delete/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Delete particular note rubric """
        data = await self.request.post()

        note_rubric_id = helpers.get_id_param_from_form_data(data)

        await auth.authentication_policy.authenticate_note_rubric_owner(self.request, note_rubric_id)

        async with self.request.app['db'].acquire() as connection:
            await db.delete_note_rubric(connection, note_rubric_id)

        return helpers.redirect_by_route_name(self.request, 'notes-rubrics')


# user partition


# # registration


class UserRegistration(aiohttp.web.View):
    """ View for '/user/register/ url """

    @aiohttp_jinja2.template('sign_up.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """ Return page with user registration form """
        return {}

    async def post(self) -> Union[aiohttp.web.HTTPSeeOther, aiohttp.web.HTTPFound]:
        """ Handle user registration form """
        data = await self.request.post()

        try:
            user = validators.UserCreation(**data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='user-register'
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                try:
                    await auth.authorization.register_user(connection, user)
                except auth.RegistrationError as error:
                    return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                        self.request, error, redirect_route_name='user-register'
                    )
                else:
                    await auth.authorization.authorize_user(connection, self.request, user)

                    return helpers.redirect_by_route_name(self.request, 'notes', is_safe=True)


# # authorization


class UserAuthorization(aiohttp.web.View):
    """ View for '/user/login/ url """

    @aiohttp_jinja2.template('sign_in.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """ Return page with user authorization form """
        return {}

    async def post(self):
        """ Handle user authorization form """
        data = await self.request.post()

        try:
            user = validators.UserAuthorization(**data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='user-login'
            )
        else:
            try:
                async with self.request.app['db'].acquire() as connection:
                    await auth.authorization.authorize_user(connection, self.request, user)
            except auth.AuthorizationError as error:
                return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                    self.request, error, redirect_route_name='user-login'
                )
            else:
                return helpers.redirect_by_route_name(self.request, 'notes', is_safe=True)


# # logout


class UserLogout(aiohttp.web.View):
    """ View for '/user/logout/' url """

    async def get(self) -> aiohttp.web.HTTPFound:
        """ Logout user """
        await auth.authorization.logout_user(self.request)

        return helpers.redirect_by_route_name(self.request, 'index')


# class UserSettingsEditing(aiohttp.web.View):
#     """ View class for '/user/settings/edit/ url. Implement GET and POST requests. """
#     # @aiohttp_jinja2.template('post_creation_form.html')
#     async def get(self) -> dict:
#         """ View for '/user/settings/edit/' url {GET} """
#         return {}
#
#     async def post(self):
#         """ View for '/user/settings/edit/' url {POST} """
#         return {}


# posts < --- > user partition


# # user (self) posts


class UserPosts(aiohttp.web.View):
    """ View for '/my/posts/' url """

    @aiohttp_jinja2.template('user_posts.html')
    @helpers.put_additional_data_in_view_result
    async def get(self) -> dict:
        """ Return page with user posts """
        url_params = self.request.rel_url.query
        validated_url_params = validators.PostUrlParams(**url_params)

        session = await aiohttp_session.get_session(self.request)
        user_id = session['user']['id']

        async with self.request.app['db'].acquire() as connection:
            posts = await db.fetch_all_posts(connection, validated_url_params, user_id=user_id)
            possible_pages_quantity = await db.fetch_posts_possible_pages_quantity(
                connection, validated_url_params, user_id=user_id
            )

        pagination_data = pagination.Pagination(possible_pages_quantity, validated_url_params.page).pagination_data

        data = {
            'posts': posts,
            'pagination': pagination_data,
        }

        return data
