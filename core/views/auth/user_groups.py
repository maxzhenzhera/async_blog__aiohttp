"""
Contains classes that implement roles of user.

Hierarchy of grants:
- `admin`           (control (create and delete) moderators;    + `moderator` rights)
    - `moderator`   (control (delete) users' posts;             + `user` rights)
        - `user`    (control self posts (create, update, delete), ability to control notes (personal marks))
- `visitor`         (not like a grant, but like the type of grants hierarchy, unauthorized, ability to read posts)

.. class:: UserGroup(abc.ABC)
    Abstract class for user group implementing
.. class:: Visitor(UserGroup)
    Unauthorized user
.. class:: UserCreation(UserGroup)
    Authorized user
.. class:: Moderator(UserCreation)
    UserCreation with moderator grant
.. class:: Admin(Moderator)
    UserCreation with admin grant
"""

import abc


class UserGroup(abc.ABC):
    """ Abstract user group """


class Visitor(UserGroup):
    """ Unauthorized user """


class User(UserGroup):
    """ Authorized user """


class Moderator(User):
    """ UserCreation with moderator grant """


class Admin(Moderator):
    """ UserCreation with admin grant """
