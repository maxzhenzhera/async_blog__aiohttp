"""
Contains views.

.. class:: Index(aiohttp.web.View)
    VIEW CLASS
.. class:: Contacts(aiohttp.web.View)
    VIEW CLASS
.. class:: Posts(aiohttp.web.View)
    VIEW CLASS
.. class:: Post(aiohttp.web.View)
    VIEW CLASS
.. class:: RandomPost(aiohttp.web.View)
    VIEW CLASS
.. class:: PostCreation(aiohttp.web.View)
    VIEW CLASS
.. class:: PostEditingForm(aiohttp.web.View)
    VIEW CLASS
.. class:: PostEditing(aiohttp.web.View)
    VIEW CLASS
.. class:: PostDeleting(aiohttp.web.View)
    VIEW CLASS
.. class:: PostRubrics(aiohttp.web.View)
    VIEW CLASS
.. class:: PostRubricCreation(aiohttp.web.View)
    VIEW CLASS
.. class:: PostRubricEditingForm(aiohttp.web.View)
    VIEW CLASS
.. class:: PostRubricEditing(aiohttp.web.View)
    VIEW CLASS
.. class:: PostRubricDeleting(aiohttp.web.View)
    VIEW CLASS
.. class:: Notes(aiohttp.web.View)
    VIEW CLASS
.. class:: Note(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteCreation(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteEditingForm(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteEditing(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteDeleting(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteRubrics(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteRubricCreation(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteRubricEditingForm(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteRubricEditing(aiohttp.web.View)
    VIEW CLASS
.. class:: NoteRubricDeleting(aiohttp.web.View)
    VIEW CLASS
.. class:: UserRegistration(aiohttp.web.View)
    VIEW CLASS
.. class:: UserAuthorization(aiohttp.web.View)
    VIEW CLASS
.. class:: UserLogout(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditing(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditingLoginForm(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditingLogin(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditingPasswordForm(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditingPassword(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditingInfoForm(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditingInfo(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditingImageForm(aiohttp.web.View)
    VIEW CLASS
.. class:: UserSettingsEditingImage(aiohttp.web.View)
    VIEW CLASS
.. class:: UserPosts(aiohttp.web.View)
    VIEW CLASS
.. class:: Thinker(aiohttp.web.View)
    VIEW CLASS
.. class:: SettingModeratorByAdmin(aiohttp.web.View)
    VIEW CLASS
.. class:: UnsettingModeratorByAdmin(aiohttp.web.View)
    VIEW CLASS
.. class:: PostModerating(aiohttp.web.View)
    VIEW CLASS
"""

from typing import Union

import aiohttp.web
import aiohttp_jinja2
import pydantic

from . import (
    InvalidFormDataError,
    auth,
    pagination,
    helpers,
    utils
)
from .. import security
from ..database import db, validators
from ..settings import USER_IMAGES_DIR


# USER_IMAGES_DIR = STATIC_DIR / USER_IMAGES_DIRECTORY_NAME


# aiohttp_jinja use `/` separator on paths joining, so I continue use `/`
# on file path argument for rendering


# main partition


class Index(aiohttp.web.View):
    """ View for '/' url """

    @aiohttp_jinja2.template('main/index.html')
    @helpers.put_session_data_in_view_result
    async def get(self) -> dict:
        """ Return index page """
        return {}


class Contacts(aiohttp.web.View):
    """ View for '/contacts/' url """

    @aiohttp_jinja2.template('main/contacts.html')
    @helpers.put_session_data_in_view_result
    async def get(self) -> dict:
        """ Return contacts page """
        return {}


# posts partition

# # posts

class Posts(aiohttp.web.View):
    """ View for '/posts/' url """

    @aiohttp_jinja2.template('posts/posts.html')
    @helpers.put_session_data_in_view_result
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

    @aiohttp_jinja2.template('posts/post.html')
    @helpers.put_session_data_in_view_result
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

    @aiohttp_jinja2.template('posts/post.html')
    @helpers.put_session_data_in_view_result
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

    @aiohttp_jinja2.template('posts/post_creation.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
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

        user_id = await helpers.get_user_id_from_session(self.request)

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

    @aiohttp_jinja2.template('posts/post_editing.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
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

    @aiohttp_jinja2.template('post_rubrics/post_rubrics.html')
    @helpers.put_session_data_in_view_result
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

    @aiohttp_jinja2.template('post_rubrics/post_rubric_creation.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def get(self) -> dict:
        """ Return page with post rubric creation form """
        return {}

    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def post(self):
        """ View for '/posts/rubrics/create/' url """
        data = await self.request.post()

        user_id = await helpers.get_user_id_from_session(self.request)

        try:
            post_rubric = validators.PostRubricCreation(user_id=user_id, **data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='posts-rubrics-create'
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.insert_post_rubric(connection, post_rubric)

            return helpers.redirect_by_route_name(self.request, 'posts-rubrics')


class PostRubricEditingForm(aiohttp.web.View):
    """ View class for '/posts/rubrics/<id: int>/edit/' url """

    @aiohttp_jinja2.template('post_rubrics/post_rubric_editing.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
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
                self.request, error, redirect_route_name='posts-rubrics-edit', id=post_rubric_id
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

    @aiohttp_jinja2.template('notes/notes.html')
    @helpers.put_session_data_in_view_result
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

        user_id = await helpers.get_user_id_from_session(self.request)

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

    @aiohttp_jinja2.template('notes/note.html')
    @helpers.put_session_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with particular note """
        note_id = helpers.get_id_param_from_url(self.request)

        _, note = await auth.authentication_policy.authenticate_note_owner(self.request, note_id)

        data = {
            'note': note
        }

        return data


class NoteCreation(aiohttp.web.View):
    """ View for '/notes/create/' url """

    @aiohttp_jinja2.template('notes/note_creation.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with note creation form """
        user_id = await helpers.get_user_id_from_session(self.request)

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

        user_id = await helpers.get_user_id_from_session(self.request)

        try:
            note = validators.NoteCreation(user_id=user_id, **data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='notes-create'
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.insert_note(connection, note)

            return helpers.redirect_by_route_name(self.request, 'notes')


class NoteEditingForm(aiohttp.web.View):
    """ View for '/notes/<id: int>/edit/' url """

    @aiohttp_jinja2.template('notes/note_editing.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ View for '/notes/{id}/edit/' url """
        note_id = helpers.get_id_param_from_url(self.request)

        user_id, note = await auth.authentication_policy.authenticate_note_owner(self.request, note_id)

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

            return helpers.redirect_by_route_name(self.request, 'notes-id', id=note_id)


class NoteDeleting(aiohttp.web.View):
    """ View for '/notes/delete/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Delete particular note """
        data = await self.request.post()

        note_id = helpers.get_id_param_from_form_data(data)

        await auth.authentication_policy.authenticate_note_owner(self.request, note_id)

        async with self.request.app['db'].acquire() as connection:
            await db.delete_note(connection, note_id)

        return helpers.redirect_by_route_name(self.request, 'notes')


# # note rubrics


class NoteRubrics(aiohttp.web.View):
    """ View for '/notes/rubrics/' url """

    @aiohttp_jinja2.template('note_rubrics/note_rubrics.html')
    @helpers.put_session_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with not rubrics """
        user_id = await helpers.get_user_id_from_session(self.request)

        async with self.request.app['db'].acquire() as connection:
            rubrics = await db.fetch_all_note_rubrics(connection, user_id)

        data = {
            'rubrics': rubrics
        }

        return data


class NoteRubricCreation(aiohttp.web.View):
    """ View for '/notes/rubrics/create/' url """

    @aiohttp_jinja2.template('note_rubrics/note_rubric_creation.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with note rubric creation form """
        return {}

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def post(self):
        """ Handle note rubric creation form """
        data = await self.request.post()

        user_id = await helpers.get_user_id_from_session(self.request)

        try:
            note_rubric = validators.NoteRubricCreation(user_id=user_id, **data)
        except pydantic.ValidationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='notes-rubrics-create'
            )
        else:
            async with self.request.app['db'].acquire() as connection:
                await db.insert_note_rubric(connection, note_rubric)

            return helpers.redirect_by_route_name(self.request, 'notes-rubrics')


class NoteRubricEditingForm(aiohttp.web.View):
    """ View for '/notes/rubrics/<id: int>/edit/' url """

    @aiohttp_jinja2.template('note_rubrics/note_rubric_editing.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with note rubric editing form """
        note_rubric_id = helpers.get_id_param_from_url(self.request)

        _, note_rubric = await auth.authentication_policy.authenticate_note_rubric_owner(self.request, note_rubric_id)

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

    @aiohttp_jinja2.template('user/sign_up.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.Visitor)
    async def get(self) -> dict:
        """ Return page with user registration form """
        return {}

    @auth.session.user_group_access_required(user_group=auth.user_groups.Visitor)
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

    @aiohttp_jinja2.template('user/sign_in.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.Visitor)
    async def get(self) -> dict:
        """ Return page with user authorization form """
        return {}

    @auth.session.user_group_access_required(user_group=auth.user_groups.Visitor)
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

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> aiohttp.web.HTTPFound:
        """ Logout user """
        await auth.authorization.logout_user(self.request)

        return helpers.redirect_by_route_name(self.request, 'index')


# # settings


class UserSettingsEditing(aiohttp.web.View):
    """ View for '/my/settings/edit/' url """

    @aiohttp_jinja2.template('user/user_settings_editing.html')
    @helpers.put_session_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with links on more narrow editing forms """
        user_id = await helpers.get_user_id_from_session(self.request)

        async with self.request.app['db'].acquire() as connection:
            user = await db.fetch_one_user(connection, user_id=user_id)

        data = {
            'user': user
        }

        return data


class UserSettingsEditingLoginForm(aiohttp.web.View):
    """ View for '/my/settings/edit/login/' url """

    @aiohttp_jinja2.template('user/user_settings_editing_login.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with links on more narrow editing forms """
        return {}


class UserSettingsEditingLogin(aiohttp.web.View):
    """ View for '/my/settings/edit/login/' url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    @utils.handle_local_error(except_error=KeyError, raise_error=InvalidFormDataError)
    async def post(self):
        """ Handle user login editing form """
        data = await self.request.post()

        password_for_verifying = data['password']

        try:
            user = await auth.authentication_policy.authenticate_user_by_password(self.request, password_for_verifying)
        except auth.AuthenticationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='user-settings-edit-login'
            )
        else:
            try:
                new_login = validators.UserSettingsEditingLogin(**data).new_login
            except pydantic.ValidationError as error:
                return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                    self.request, error, redirect_route_name='user-settings-edit-login'
                )
            else:
                current_login = user['login']

                if new_login == current_login:
                    error = 'it seems no sense to change login with no difference with current'
                    return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                        self.request, error, redirect_route_name='user-settings-edit-login'
                    )

                async with self.request.app['db'].acquire() as connection:
                    login_availability = await auth.authorization.check_login_for_availability(connection, new_login)

                if login_availability:
                    user_id = user['id']

                    await db.update_user_login(connection, user_id, new_login)

                    return helpers.redirect_by_route_name(self.request, 'thinker-id', id=user_id)
                else:
                    error = 'Login is busy. Choose another, please!'
                    return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                        self.request, error, redirect_route_name='user-settings-edit-login'
                    )


class UserSettingsEditingPasswordForm(aiohttp.web.View):
    """ View for '/my/settings/edit/password' url """

    @aiohttp_jinja2.template('user/user_settings_editing_password.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with user password editing form """
        return {}


class UserSettingsEditingPassword(aiohttp.web.View):
    """ View for '/user/settings/edit/password/ url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    @utils.handle_local_error(except_error=KeyError, raise_error=InvalidFormDataError)
    async def post(self):
        """ Handle user password editing form """
        data = await self.request.post()

        password_for_verifying = data['password']

        try:
            user = await auth.authentication_policy.authenticate_user_by_password(self.request, password_for_verifying)
        except auth.AuthenticationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='user-settings-edit-password'
            )
        else:
            try:
                new_password = validators.UserSettingsEditingPassword(**data).new_password
            except pydantic.ValidationError as error:
                return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                    self.request, error, redirect_route_name='user-settings-edit-password'
                )
            else:
                user_id = user['id']
                new_hashed_password = security.hash_password(new_password)

                async with self.request.app['db'].acquire() as connection:
                    await db.update_user_password(connection, user_id, new_hashed_password)

                return helpers.redirect_by_route_name(self.request, 'thinker-id', id=user_id)


class UserSettingsEditingInfoForm(aiohttp.web.View):
    """ View for '/my/settings/edit/info/' url """

    @aiohttp_jinja2.template('user/user_settings_editing_info.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with links on more narrow editing forms """
        return {}


class UserSettingsEditingInfo(aiohttp.web.View):
    """ View for '/user/settings/edit/info/ url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    @utils.handle_local_error(except_error=KeyError, raise_error=InvalidFormDataError)
    async def post(self):
        """ Handle user info settings editing form """
        data = await self.request.post()

        password_for_verifying = data['password']

        try:
            user = await auth.authentication_policy.authenticate_user_by_password(self.request, password_for_verifying)
        except auth.AuthenticationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='user-settings-edit-info'
            )
        else:
            try:
                new_info = validators.UserSettingsEditingInfo(**data)
            except pydantic.ValidationError as error:
                return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                    self.request, error, redirect_route_name='user-settings-edit-info'
                )
            else:
                user_id = user['id']

                async with self.request.app['db'].acquire() as connection:
                    await db.update_user_info(connection, user_id, new_info)

                return helpers.redirect_by_route_name(self.request, 'thinker-id', id=user_id)


class UserSettingsEditingImageForm(aiohttp.web.View):
    """ View for '/my/settings/edit/image/' url """

    @aiohttp_jinja2.template('user/user_settings_editing_image.html')
    @helpers.put_session_data_in_view_result(put_alert_message=True)
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with user image editing form """
        user_id = await helpers.get_user_id_from_session(self.request)

        async with self.request.app['db'].acquire() as connection:
            user = await db.fetch_one_user(connection, user_id=user_id)

        data = {
            'user': user
        }

        return data


class UserSettingsEditingImage(aiohttp.web.View):
    """ View for '/user/settings/edit/image/ url """

    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    @utils.handle_local_error(except_error=AssertionError, raise_error=InvalidFormDataError)
    async def post(self):
        """ Handle user image editing form """
        reader = await self.request.multipart()

        password_field = await reader.next()
        assert password_field.name == 'password'
        password_for_verifying = await password_field.text()

        try:
            user = await auth.authentication_policy.authenticate_user_by_password(self.request, password_for_verifying)
        except auth.AuthenticationError as error:
            return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                self.request, error, redirect_route_name='user-settings-edit-image'
            )
        else:
            user_id = user['id']

            # absolute image path - for saving or deleting on hard drive
            image_name = f'{user_id}.png'
            image_path_for_saving_on_hard_drive = USER_IMAGES_DIR / image_name

            image_field = await reader.next()
            assert image_field.name == 'image'
            image_field_filename = image_field.filename
            # assert that field non empty by filename presence
            is_image_uploaded = bool(image_field_filename)

            if is_image_uploaded:
                try:
                    _ = validators.FileIsImage(filename=image_field_filename)
                except pydantic.ValidationError as error:
                    return await helpers.redirect_back_to_the_form_with_alert_message_in_session(
                        self.request, error, redirect_route_name='user-settings-edit-image'
                    )
                else:
                    # relative image path - for saving static url in db
                    image_path_for_saving_static_url_in_db = image_path_for_saving_on_hard_drive.relative_to(
                        # ../static/ | images/user_images/image_name
                        image_path_for_saving_on_hard_drive.parent.parent.parent
                    ).as_posix()

                    await helpers.save_user_image(image_path_for_saving_on_hard_drive, image_field)

                    async with self.request.app['db'].acquire() as connection:
                        await db.update_user_image_path(connection, user_id, image_path_for_saving_static_url_in_db)

            is_set_default_image_field = await reader.next()
            if is_set_default_image_field:
                if not is_image_uploaded:
                    await helpers.delete_user_image(image_path_for_saving_on_hard_drive)

                    async with self.request.app['db'].acquire() as connection:
                        await db.update_user_image_path(connection, user_id, None)

            return helpers.redirect_by_route_name(self.request, 'thinker-id', id=user_id)


# posts < --- > user partition


# # user (self) posts


class UserPosts(aiohttp.web.View):
    """ View for '/my/posts/' url """

    @aiohttp_jinja2.template('posts/user_posts.html')
    @helpers.put_session_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.User)
    async def get(self) -> dict:
        """ Return page with user posts """
        url_params = self.request.rel_url.query
        validated_url_params = validators.PostUrlParams(**url_params)

        user_id = await helpers.get_user_id_from_session(self.request)

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


# thinker partition


# # thinker page


class Thinker(aiohttp.web.View):
    """ View for '/thinker/<id: int>/' url """

    @aiohttp_jinja2.template('user/user_page.html')
    @helpers.put_session_data_in_view_result
    async def get(self):
        """ Return page with thinker info """
        user_id = helpers.get_id_param_from_url(self.request)

        async with self.request.app['db'].acquire() as connection:
            user = await db.fetch_one_user(connection, user_id=user_id)

        data = {
            'user': user
        }

        return data


# grant user partition


# # admin


# # - set moderator


class SettingModeratorByAdmin(aiohttp.web.View):
    """ View for '/admin/set/moderator/' url """

    @aiohttp_jinja2.template('admin/moderator_setting.html')
    @helpers.put_session_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def get(self) -> dict:
        """ Return page with setting moderator form """
        return {}

    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def post(self):
        """ Handle setting moderator form """
        data = await self.request.post()

        user_id = helpers.get_id_param_from_form_data(data)

        async with self.request.app['db'].acquire() as connection:
            await db.add_user_in_moderators(connection, user_id)

        return helpers.redirect_by_route_name(self.request, 'admin-unset-moderator')


# # - unset moderator


class UnsettingModeratorByAdmin(aiohttp.web.View):
    """ View for '/admin/unset/moderator/' url """

    @aiohttp_jinja2.template('admin/moderator_unsetting.html')
    @helpers.put_session_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def get(self) -> dict:
        """ Return page with unsetting moderator form """
        async with self.request.app['db'].acquire() as connection:
            moderators = await db.fetch_all_moderators(connection)

        data = {
            'moderators': moderators
        }

        return data

    @auth.session.user_group_access_required(user_group=auth.user_groups.Admin)
    async def post(self):
        """ Handle unsetting moderator form """
        data = await self.request.post()

        user_id = helpers.get_id_param_from_form_data(data)

        async with self.request.app['db'].acquire() as connection:
            await db.delete_user_from_moderators(connection, user_id)

        return helpers.redirect_by_route_name(self.request, 'admin-unset-moderator')


# # moderator


# # - moderate posts


class PostModerating(aiohttp.web.View):
    """ View for '/moderator/posts/delete/' url """

    @aiohttp_jinja2.template('moderator/post_deleting.html')
    @helpers.put_session_data_in_view_result
    @auth.session.user_group_access_required(user_group=auth.user_groups.Moderator)
    async def get(self):
        """ Return form for post moderating [deleting] """
        return {}

    @auth.session.user_group_access_required(user_group=auth.user_groups.Moderator)
    async def post(self):
        """ Handle post moderating form [deleting] """
        data = await self.request.post()

        post_id = helpers.get_id_param_from_form_data(data)

        async with self.request.app['db'].acquire() as connection:
            await db.delete_post(connection, post_id)

        return helpers.redirect_by_route_name(self.request, 'posts')
