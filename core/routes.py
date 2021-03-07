"""
Contains route-functions that setup routes in the app.

.. function:: setup_routes(app: aiohttp.web.Application) -> None
    Setup routes in the app
.. function:: setup_static_routes(app: aiohttp.web.Application) -> None
    Setup static route in the app

.. const:: PROJECT_ROOT
    Contains path to project directory
"""

import aiohttp.web

from .views import views
from .settings import STATIC_DIR


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
    app.router.add_get('/my/settings/edit/', views.UserSettingsEditing, name='user-settings-edit')
    app.router.add_get(
        '/my/settings/edit/login/', views.UserSettingsEditingLoginForm, name='user-settings-edit-login'
    )
    app.router.add_get(
        '/my/settings/edit/password/', views.UserSettingsEditingPasswordForm, name='user-settings-edit-password'
    )
    app.router.add_get(
        '/my/settings/edit/info/', views.UserSettingsEditingInfoForm, name='user-settings-edit-info'
    )
    app.router.add_get(
        '/my/settings/edit/image/', views.UserSettingsEditingImageForm, name='user-settings-edit-image'
    )
    # # # POST
    app.router.add_post('/user/settings/edit/login/', views.UserSettingsEditingLogin)
    app.router.add_post('/user/settings/edit/password/', views.UserSettingsEditingPassword)
    app.router.add_post('/user/settings/edit/info/', views.UserSettingsEditingInfo)
    app.router.add_post('/user/settings/edit/image/', views.UserSettingsEditingImage)

    # posts < --- > user partition
    # # user (self) posts
    # # # GET
    app.router.add_get('/my/posts/', views.UserPosts, name='user-posts')

    # thinker partition
    # # thinker page
    # # # GET
    app.router.add_get(r'/thinker/{id:\d+}/', views.Thinker, name='thinker-id')

    # grant user partition
    # # admin
    # # - set moderator
    # # # GET
    app.router.add_get('/admin/set/moderator/', views.SettingModeratorByAdmin, name='admin-set-moderator')
    # # # POST
    app.router.add_post('/admin/set/moderator/', views.SettingModeratorByAdmin)
    # # - unset moderator
    # # # GET
    app.router.add_get('/admin/unset/moderator/', views.UnsettingModeratorByAdmin, name='admin-unset-moderator')
    # # # POST
    app.router.add_post('/admin/unset/moderator/', views.UnsettingModeratorByAdmin)

    # # moderator
    # # - moderate posts
    # # # GET
    app.router.add_get(r'/moderator/posts/delete/', views.PostModerating, name='moderator-posts-delete')
    # # # POST
    app.router.add_post(r'/moderator/posts/delete/', views.PostModerating)

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

    static_root_url = '/static/'

    # for jinja `static` function
    app['static_root_url'] = static_root_url

    app.router.add_static(
        static_root_url,
        path=STATIC_DIR,
        name='static'
    )
