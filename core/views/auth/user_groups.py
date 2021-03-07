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

.. const:: VISITOR_USER_GROUP_ID
    Special id for user group
.. const:: USER_USER_GROUP_ID
    Special id for user group
.. const:: MODERATOR_USER_GROUP_ID
    Special id for user group
.. const:: ADMIN_USER_GROUP_ID
    Special id for user group
..const:: user_groups_mapping
    Mapping that contains pairs - int id key and user group class
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


# CLASSES ARE NOT SERIALIZABLE [FOR JSON] -> IN THE SESSION SAVE ID OF THE USER GROUP CLASS
VISITOR_USER_GROUP_ID = 1
USER_USER_GROUP_ID = 2
MODERATOR_USER_GROUP_ID = 3
ADMIN_USER_GROUP_ID = 4

user_groups_mapping = {
    VISITOR_USER_GROUP_ID: Visitor,
    USER_USER_GROUP_ID: User,
    MODERATOR_USER_GROUP_ID: Moderator,
    ADMIN_USER_GROUP_ID: Admin
}
