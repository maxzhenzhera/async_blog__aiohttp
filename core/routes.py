"""
Contains route-functions that setup routes in the app.


Functions:
    def setup_routes(app: aiohttp.web.Application) -> None:
    = setup routes in the app
    --------------------------------------------------------------------------------------------------------------------
    def setup_static_routes(app: aiohttp.web.Application) -> None:
    = setup static route in the app
    --------------------------------------------------------------------------------------------------------------------
Vars:
    BASE_DIR: pathlib.Path = contains path to project directory
    --------------------------------------------------------------------------------------------------------------------
"""

import pathlib

import aiohttp.web

from core.views import views


PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app: aiohttp.web.Application) -> None:
    """ Setup routes in the app """
    # main partition
    app.router.add_get('/', views.index, name='index')
    app.router.add_get('/contacts/', views.contacts, name='contacts')

    # posts partition
    app.router.add_get('/posts/', views.posts, name='posts')
    app.router.add_get('/posts/create/', views.PostCreation, name='posts-create')
    app.router.add_get('/posts/rubrics/', views.post_rubrics, name='posts-rubrics')
    app.router.add_get('/posts/rubrics/create/', views.PostRubricEditing, name='posts-rubrics-create')
    app.router.add_get(r'/posts/random/', views.random_post, name='posts-random')
    app.router.add_get(r'/posts/{id:\d+}/', views.post, name='posts-id')
    app.router.add_get(r'/posts/{id:\d+}/edit/', views.PostEditing, name='posts-id-edit')
    app.router.add_get(r'/posts/rubrics/{id:\d+}/edit/', views.PostRubricEditing, name='posts-rubrics-id-edit')

    app.router.add_post('/posts/create/', views.PostCreation)
    app.router.add_post('/posts/rubrics/create/', views.PostRubricCreation)
    app.router.add_post(r'/posts/{id:\d+}/edit/', views.PostEditing)
    app.router.add_post(r'/posts/rubrics/{id:\d+}/edit/', views.PostRubricEditing)

    # notes partition
    app.router.add_get('/notes/', views.notes, name='notes')
    app.router.add_get('/notes/create/', views.NoteCreation, name='notes-create')
    app.router.add_get('/notes/rubrics/', views.note_rubrics, name='notes-rubrics')
    app.router.add_get('/notes/rubrics/create/', views.NoteRubricCreation, name='notes-rubrics-create')
    app.router.add_get(r'/notes/{id:\d+}/', views.note, name='notes-id')
    app.router.add_get(r'/notes/{id:\d+}/edit/', views.NoteEditing, name='notes-id-edit')
    app.router.add_get(r'/notes/rubrics/{id:\d+}/edit/', views.NoteRubricEditing, name='notes-rubrics-id-edit')

    app.router.add_post('/notes/create/', views.NoteCreation)
    app.router.add_post('/notes/rubrics/create/', views.NoteRubricCreation)
    app.router.add_post(r'/notes/{id:\d+}/edit/', views.NoteEditing)
    app.router.add_post(r'/notes/rubrics/{id:\d+}/edit/', views.NoteRubricEditing)

    # user partition
    app.router.add_get('/user/register/', views.UserRegistration, name='user-register')
    app.router.add_get('/user/login/', views.UserAuthorization, name='user-login')
    app.router.add_get('/user/logout/', views.user_logout, name='user-logout')
    app.router.add_get('/user/settings/edit', views.UserSettingsEditing, name='user-settings')

    app.router.add_post('/user/register/', views.UserRegistration)
    app.router.add_post('/user/login/', views.UserAuthorization)
    app.router.add_post('/user/settings/edit/', views.UserSettingsEditing)

    # posts < --- > user partition
    app.router.add_get('/my/posts/', views.user_posts, name='my-posts')

    # static
    setup_static_routes(app)


def setup_static_routes(app: aiohttp.web.Application) -> None:
    """ Setup static route in the app """
    app.router.add_static(
        '/static/',
        path=PROJECT_ROOT / 'static',
        name='static'
    )
