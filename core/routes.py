"""
Contains route-functions that setup routes in the app.

.. function:: setup_routes(app: aiohttp.web.Application) -> None
    Setup routes in the app
.. function:: setup_static_routes(app: aiohttp.web.Application) -> None:
    Setup static route in the app

.. const:: PROJECT_ROOT
    Contains path to project directory
"""

import pathlib

import aiohttp.web

from .views import views


# `core` package
PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app: aiohttp.web.Application) -> None:
    """
    Setup routes in the app.

    :param app: instance of the web application
    :type app: aiohttp.web.Application

    :return: None
    :rtype: None
    """

    # main partition
    app.router.add_get('/', views.Index, name='index')
    app.router.add_get('/contacts/', views.Contacts, name='contacts')

    # posts partition
    # # posts
    # # # GET
    app.router.add_get('/posts/', views.Posts, name='posts')
    app.router.add_get('/posts/random/', views.RandomPost, name='posts-random')
    app.router.add_get('/posts/create/', views.PostCreation, name='posts-create')
    app.router.add_get(r'/posts/{id:\d+}/', views.Post, name='posts-id')
    app.router.add_get(r'/posts/{id:\d+}/edit/', views.PostEditingForm, name='posts-id-edit')
    # # # POST
    app.router.add_post('/posts/create/', views.PostCreation)
    app.router.add_post('/posts/edit/', views.PostEditing)
    app.router.add_post('/posts/delete/', views.PostDeleting)
    # # post rubrics    [ONLY ADMIN HAS ABILITY TO CONTROL POST RUBRICS]
    # # # GET
    app.router.add_get('/posts/rubrics/', views.PostRubrics, name='posts-rubrics')
    app.router.add_get('/posts/rubrics/create/', views.PostRubricCreation, name='posts-rubrics-create')
    app.router.add_get(r'/posts/rubrics/{id:\d+}/edit/', views.PostRubricEditingForm, name='posts-rubrics-id-edit')
    # # # POST
    app.router.add_post('/posts/rubrics/create/', views.PostRubricCreation)
    app.router.add_post('/posts/rubrics/edit/', views.PostRubricEditing)
    app.router.add_post('/posts/rubrics/delete/', views.PostRubricDeleting)

    # notes partition
    # # notes
    # # # GET
    app.router.add_get('/notes/', views.Notes, name='notes')
    app.router.add_get('/notes/create/', views.NoteCreation, name='notes-create')
    app.router.add_get(r'/notes/{id:\d+}/', views.Note, name='notes-id')
    app.router.add_get(r'/notes/{id:\d+}/edit/', views.NoteEditingForm, name='notes-id-edit')
    # # # POST
    app.router.add_post('/notes/create/', views.NoteCreation)
    app.router.add_post('/notes/edit/', views.NoteEditing)
    app.router.add_post('/notes/delete/', views.NoteDeleting)
    # # note rubrics
    # # # GET
    app.router.add_get('/notes/rubrics/', views.NoteRubrics, name='notes-rubrics')
    app.router.add_get('/notes/rubrics/create/', views.NoteRubricCreation, name='notes-rubrics-create')
    app.router.add_get(r'/notes/rubrics/{id:\d+}/edit/', views.NoteRubricEditingForm, name='notes-rubrics-id-edit')
    # # # POST
    app.router.add_post('/notes/rubrics/create/', views.NoteRubricCreation)
    app.router.add_post('/notes/rubrics/edit/', views.NoteRubricEditing)
    app.router.add_post('/notes/rubrics/delete/', views.NoteRubricDeleting)

    # user partition
    # # registration
    # # # GET
    app.router.add_get('/user/register/', views.UserRegistration, name='user-register')
    # # # POST
    app.router.add_post('/user/register/', views.UserRegistration)
    # # authorization
    # # # GET
    app.router.add_get('/user/login/', views.UserAuthorization, name='user-login')
    # # # POST
    app.router.add_post('/user/login/', views.UserAuthorization)
    # # logout
    app.router.add_get('/user/logout/', views.UserLogout, name='user-logout')
    # # settings
    # # # # GET
    # app.router.add_get('/my/settings/edit', views.UserSettingsEditingForm, name='user-settings')
    # # # # POST
    # app.router.add_post('/user/settings/edit/', views.UserSettingsEditing)

    # posts < --- > user partition
    # # user (self) posts
    # # # GET
    app.router.add_get('/my/posts/', views.UserPosts, name='user-posts')

    # # user < --- > user partition
    # # # user page
    # # # # GET
    # app.router.add_get(r'/thinker/{id:\d+}/', views.UserPosts)
    #
    # # grant user partition
    # # # admin
    # # # - delete user
    # # # # GET
    # app.router.add_get('/admin/delete/user/', views.UserPosts)
    # # # # POST
    # app.router.add_post('/admin/delete/user/', views.UserPosts)
    # # # - set moderator
    # # # # GET
    # app.router.add_get('/admin/set/moderator/', views.UserPosts)
    # # # # POST
    # app.router.add_post('/admin/set/moderator/', views.UserPosts)
    # # # - unset moderator
    # # # # GET
    # app.router.add_get('/admin/unset/moderator/', views.UserPosts)
    # # # # POST
    # app.router.add_post('/admin/unset/moderator/', views.UserPosts)
    #
    # # # moderator
    # # # - moderate posts
    # # # # GET
    # app.router.add_get(r'/moderator/posts/{id:\d+}/', views.UserPosts)
    # # # # POST
    # app.router.add_post(r'/moderator/posts/delete/', views.UserPosts)

    # - - - - - - - - - - - - -
    # static                   |
    setup_static_routes(app)


def setup_static_routes(app: aiohttp.web.Application) -> None:
    """
    Setup static route in the app.

    :param app: instance of the web application
    :type app: aiohttp.web.Application

    :return: None
    :rtype: None
    """

    app.router.add_static(
        '/static/',
        path=PROJECT_ROOT / 'static',
        name='static'
    )
