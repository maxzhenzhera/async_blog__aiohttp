"""
Contains functions that execute CRUD operations with db.

.. exception:: RecordNotFoundError(Exception)
    Raised when record in the DB is not found

.. decorator:: check_record_in_db(db_function: Callable) -> Callable

.. function:: execute_query(connection: aiomysql.Connection, query: str, params: dict) -> None
    Execute query (shortcut for execution query [insert, update, delete])
.. function:: fetch_posts_possible_pages_quantity(connection: aiomysql.Connection, params: validators.PostUrlParams,
        *args, user_id: Optional[int] = None) -> int
    Return possible page quantity for posts
.. function:: fetch_notes_possible_pages_quantity(connection: aiomysql.Connection, params: validators.NoteUrlParams,
        user_id: int) -> int
    Return possible page quantity for notes
.. function:: fetch_all_post_rubrics(connection: aiomysql.Connection) -> list[dict[str, Union[int, str]]]
    Fetch all post rubrics
.. function:: fetch_one_post_rubric(connection: aiomysql.Connection, post_rubric_id: int) -> dict[str, Union[int, str]]
    Fetch one post rubric
.. function:: fetch_all_posts(connection: aiomysql.Connection, params: validators.PostUrlParams, *args,
        user_id: Optional[int] = None) -> list[dict[str, Union[int, str, datetime.datetime]]]
    Fetch all posts
.. function:: fetch_one_post(connection: aiomysql.Connection, post_id: int
        ) -> dict[str, Union[int, str, datetime.datetime]]
    Fetch one post
.. function:: fetch_one_random_post(connection: aiomysql.Connection) -> dict[str, Union[int, str, datetime.datetime]]
    Fetch one random post
.. function:: fetch_all_note_rubrics(connection: aiomysql.Connection, user_id: int) -> list[dict[str, Union[int, str]]]
    Fetch all note rubrics
.. function:: fetch_one_note_rubric(connection: aiomysql.Connection, note_rubric_id: int) -> dict[str, Union[int, str]]
    Fetch one note rubric
.. function:: fetch_all_notes(connection: aiomysql.Connection, user_id: int, params: validators.NoteUrlParams
        ) -> list[dict[str, Union[int, str, datetime.datetime]]]
    Fetch all notes
.. function:: fetch_one_note(connection: aiomysql.Connection, note_id: int
        ) -> dict[str, Union[int, str, datetime.datetime]]
    Fetch one note
.. function:: fetch_one_user(connection: aiomysql.Connection, *args, user_id: Optional[int] = None,
        login: Optional[str] = None, password: Optional[str] = None) -> dict[str, Union[int, str]]:
    Fetch one user
.. function:: insert_post_rubric(connection: aiomysql.Connection, post_rubric: validators.PostRubricCreation) -> None
    Insert post rubric
.. function:: insert_post(connection: aiomysql.Connection, post: validators.PostCreation) -> None
    Insert post
.. function:: insert_note_rubric(connection: aiomysql.Connection, note_rubric: validators.NoteRubricCreation) -> None
    Insert note rubric
.. function:: insert_note(connection: aiomysql.Connection, note: validators.NoteCreation) -> None
    Insert note
.. function:: insert_user(connection: aiomysql.Connection, user: validators.UserCreation) -> None
    Insert user
.. function:: update_post_rubric(connection: aiomysql.Connection, post_rubric_id: int,
        post_rubric: validators.PostRubricCreation) -> None
    Update post rubric
.. function:: update_post(connection: aiomysql.Connection, post_id: int, post: validators.PostCreation) -> None
    Update post
.. function:: update_note_rubric(connection: aiomysql.Connection, note_rubric_id: int,
        note_rubric: validators.NoteRubricCreation) -> None
    Update note rubric
.. function:: update_note(connection: aiomysql.Connection, note_id: int, note: validators.NoteCreation) -> None
    Update note
.. function:: update_user(connection: aiomysql.Connection, user_id: int, user: validators.UserCreation) -> None
    Update user
.. function:: delete_post_rubric(connection: aiomysql.Connection, post_rubric_id: int) -> None
    Delete post rubric
.. function:: delete_post(connection: aiomysql.Connection, post_id: int,) -> None
    Delete post
.. function:: delete_note_rubric(connection: aiomysql.Connection, note_rubric_id: int) -> None
    Delete note rubric
.. function:: delete_note(connection: aiomysql.Connection, note_id: int,) -> None
    Delete note
.. function:: delete_user(connection: aiomysql.Connection, user_id: int) -> None
    Delete user

.. const:: jinja_sql
    Template engine for sql on Jinja basis
"""

import datetime
import math
import random
from functools import wraps
from typing import (
    Any,
    Callable,
    Optional,
    Union
)

import aiomysql
from jinjasql import JinjaSql

from . import validators

# template engine for sql on Jinja basis
jinja_sql = JinjaSql(param_style='pyformat')


class RecordNotFoundError(Exception):
    """ Raised when record in the DB is not found """


def check_record_in_db(db_function: Callable) -> Callable:
    """
    Envelopes db function to raise `RecordNotFoundError` if result is empty.

    So, all enveloped db functions might raise `RecordNotFoundError`.

    :param db_function: db function that fetch some result (where might be raised `RecordNotFoundError`)
    :type db_function: Callable

    :return: inner function
    :rtype: Callable
    """

    @wraps(db_function)
    async def inner(connection: aiomysql.Connection, *args: Any, **kwargs: Any) -> dict:
        """
        Execute db function and analyze result (raises error if result is empty).

        :param connection: db connection
        :type connection: aiomysql.Connection
        :param args: other arguments that were passed to db function
        :type args: Any
        :param kwargs: other named arguments that were passed to db function
        :type kwargs: Any

        :return: db function result
        :rtype: dict

        :raises RecordNotFoundError: raised if db function result is empty
        """

        db_function_result = await db_function(connection, *args, **kwargs)

        if not db_function_result:
            # db_function_result is empty
            raise RecordNotFoundError

        return db_function_result

    return inner


# ------------------------- HELP FUNCTIONS (SHORTCUT)


async def execute_query(connection: aiomysql.Connection, query: str, params: dict) -> None:
    """
    Execute query (might be used for insert, update, delete actions that do not fetch result - only execute).

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param query: sql query
    :type query: str
    :param params: query params
    :type params: dict

    :return: None
    :rtype: None
    """

    async with connection.cursor() as cursor:
        await cursor.execute(query, params)


# ------------------------- CRUD OPERATIONS


# # ------------------------- AGGREGATE QUERIES

async def fetch_posts_possible_pages_quantity(connection: aiomysql.Connection, params: validators.PostUrlParams,
                                              *args: Any,
                                              user_id: Optional[int] = None
                                              ) -> int:
    """
    Fetch quantity of the possible posts pages.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param params: additional params
    :type params: validators.PostUrlParams
    :keyword user_id: user id
    :type user_id: int

    :return: possible quantity of pages
    :rtype: int
    """

    query_template = """
        SELECT
            COUNT(*)
        FROM
            `posts`
        WHERE 
            1 = 1
            {% if rubric_id %}
                AND `post_rubric_id` = {{ rubric_id }}
            {% endif %}
            {% if search_word %}
                AND MATCH (`posts`.`title`, `posts`.`content`) AGAINST ({{ search_word }})
            {% endif %}
            {% if user_id %}
                AND `posts`.`user_id` = {{ user_id }}
            {% endif %}
        ;
    """
    params = params.dict(by_alias=True)
    params['user_id'] = user_id

    query, bound_params = jinja_sql.prepare_query(query_template, params)

    async with connection.cursor() as cursor:
        await cursor.execute(query, bound_params)
        query_result = await cursor.fetchone()
    posts_quantity = int(query_result[0])
    possible_pages_quantity = math.ceil(posts_quantity / params['rows_quantity'])

    return possible_pages_quantity


async def fetch_notes_possible_pages_quantity(connection: aiomysql.Connection, params: validators.NoteUrlParams,
                                              user_id: int
                                              ) -> int:
    """
    Fetch quantity of the possible posts pages.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param params: additional params
    :type params: validators.NoteUrlParams
    :param user_id: user id
    :type user_id: int

    :return: possible quantity pages
    :rtype: int
    """

    query_template = """
        SELECT 
            COUNT(*)
        FROM
            `notes`
        WHERE
            `notes`.`user_id` = {{ user_id }}
            {% if rubric_id %}
                AND `note_rubric_id` = {{ rubric_id }}
            {% endif %}
        ; 
    """
    params = params.dict(by_alias=True)
    params['user_id'] = user_id

    query, bound_params = jinja_sql.prepare_query(query_template, params)

    async with connection.cursor() as cursor:
        await cursor.execute(query, bound_params)
        query_result = await cursor.fetchone()
    posts_quantity = int(query_result[0])
    possible_pages_quantity = math.ceil(posts_quantity / params['rows_quantity'])

    return possible_pages_quantity

# # ------------------------- READ QUERIES


# # # ------------------------- Posts


async def fetch_all_post_rubrics(connection: aiomysql.Connection) -> list[dict[str, Union[int, str]]]:
    """
    Fetch all post rubrics.

    :param connection: db connection
    :type connection: aiomysql.Connection

    :return: data of the post rubric
    :rtype: list[dict[str, Union[int, str]]]
    """

    query = 'SELECT * FROM `post_rubrics`;'

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query)
        post_rubrics = await cursor.fetchall()

    return post_rubrics


@check_record_in_db
async def fetch_one_post_rubric(connection: aiomysql.Connection, post_rubric_id: int) -> dict[str, Union[int, str]]:
    """
    Fetch one post rubric.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param post_rubric_id: post rubric id
    :type post_rubric_id: int

    :return: data of the post rubric
    :rtype: dict[str, Union[int, str]]
    """

    query = 'SELECT * FROM `post_rubrics` WHERE `id` = %(post_rubric_id)s;'
    params = {
        'post_rubric_id': post_rubric_id
    }

    async with connection.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(query, params)
        post_rubric = await cursor.fetchone()

    return post_rubric


async def fetch_all_posts(connection: aiomysql.Connection, params: validators.PostUrlParams,
                          *args: Any,
                          user_id: Optional[int] = None,
                          ) -> list[dict[str, Union[int, str, datetime.datetime]]]:
    """
    Fetch all posts (considering extra arguments).

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param params: additional params
    :type params: validators.PostUrlParams
    :keyword user_id: user id
    :type user_id: int

    :return: data of the posts
    :rtype: list[dict[str, Union[int, str, datetime.datetime]]]
    """

    query_template = """
        SELECT
            `posts`.*,
            `post_rubrics`.`title` AS `rubric`
        FROM
            `posts`
                LEFT JOIN
            `post_rubrics` ON `posts`.`rubric_id` = `post_rubrics`.`id`
        WHERE 
            1 = 1
            {% if rubric_id %}
                AND `rubric_id` = {{ rubric_id }}
            {% endif %}
            {% if search_word %}
                AND MATCH (`posts`.`title`, `posts`.`content`) AGAINST ({{ search_word }})
            {% endif %}
            {% if user_id %}
                AND `posts`.`user_id` = {{ user_id }}
            {% endif %}
        ORDER BY `posts`.`created_date` DESC
        LIMIT {{ offset }}, {{ rows_quantity }}
        ;
    """
    params = params.dict(by_alias=True)
    params['user_id'] = user_id
    params['offset'] = (params['page_number'] - 1) * params['rows_quantity']

    query, bound_params = jinja_sql.prepare_query(query_template, params)

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query, bound_params)
        posts = await cursor.fetchall()

    return posts


@check_record_in_db
async def fetch_one_post(connection: aiomysql.Connection, post_id: int
                         ) -> dict[str, Union[int, str, datetime.datetime]]:
    """
    Fetch the one particular post.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param post_id: post id
    :type post_id: int

    :return: data of the post
    :rtype: dict[str, Union[int, str, datetime.datetime]]
    """

    query = """
        SELECT
            `posts`.*,
            `post_rubrics`.`title` AS `rubric`
        FROM
            `posts`
                LEFT JOIN
            `post_rubrics` ON `posts`.`rubric_id` = `post_rubrics`.`id`
        WHERE
            `posts`.`id` = %(post_id)s
        ;
    """
    params = {
        'post_id': post_id
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query, params)
        post = await cursor.fetchone()

    return post


async def fetch_one_random_post(connection: aiomysql.Connection) -> dict[str, Union[int, str, datetime.datetime]]:
    """
    Fetch an one random post.

    :param connection: db connection
    :type connection: aiomysql.Connection

    :return: data of the random post
    :rtype: dict[str, Union[int, str, datetime.datetime]]
    """

    query = """
        SELECT
            `posts`.*,
            `post_rubrics`.`title` AS `rubric`
        FROM
            `posts`
                LEFT JOIN
            `post_rubrics` ON `posts`.`rubric_id` = `post_rubrics`.`id`
        ORDER BY %(order_key)s LIMIT 1
        ;
    """
    params = {
        'order_key': random.random()
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query, params)
        post = await cursor.fetchone()

    return post


# # # ------------------------- Notes


async def fetch_all_note_rubrics(connection: aiomysql.Connection, user_id: int) -> list[dict[str, Union[int, str]]]:
    """
    Fetch all notes by rubric.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param user_id: user id
    :type user_id: int

    :return: data of the note rubrics
    :rtype: list[dict[str, Union[int, str]]]
    """

    query = 'SELECT * FROM `note_rubrics` WHERE `user_id` = %(user_id)s ORDER BY `edited_date` DESC;'
    params = {
        'user_id': user_id
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query, params)
        note_rubrics = await cursor.fetchall()

    return note_rubrics


@check_record_in_db
async def fetch_one_note_rubric(connection: aiomysql.Connection, note_rubric_id: int) -> dict[str, Union[int, str]]:
    """
    Fetch all notes by rubric.

    :param connection: db conncetion
    :type connection: aiomysql.Connection
    :param note_rubric_id: note rubric id
    :type note_rubric_id: int

    :return: data of the note rubric
    :rtype: dict[str, Union[int, str]]
    """

    query = 'SELECT * FROM `note_rubrics` WHERE `id` = %(note_rubric_id)s;'
    params = {
        'note_rubric_id': note_rubric_id
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query, params)
        note_rubric = await cursor.fetchone()

    return note_rubric


async def fetch_all_notes(connection: aiomysql.Connection, user_id: int, params: validators.NoteUrlParams
                          ) -> list[dict[str, Union[int, str, datetime.datetime]]]:
    """
    Fetch all notes (considering extra arguments).

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param user_id: user id
    :type user_id: int
    :param params: additional params
    :type params: validators.NoteUrlParams

    :return: data of the notes
    :rtype: list[dict[str, Union[int, str, datetime.datetime]]]
    """

    query_template = """
        SELECT 
            `notes`.*, 
            `note_rubrics`.title AS `rubric`
        FROM
            `notes`
                LEFT JOIN
            `note_rubrics` ON `notes`.`rubric_id` = `note_rubrics`.`id`
        WHERE
            `notes`.`user_id` = {{ user_id }}
            {% if rubric_id %}
                AND `rubric_id` = {{ rubric_id }}
            {% endif %}
        LIMIT {{ offset }}, {{ rows_quantity }}
        ; 
    """
    params = params.dict(by_alias=True)
    params['user_id'] = user_id
    params['offset'] = (params['page_number'] - 1) * params['rows_quantity']

    query, bound_params = jinja_sql.prepare_query(query_template, params)

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query,bound_params)
        notes = await cursor.fetchall()

    return notes


@check_record_in_db
async def fetch_one_note(connection: aiomysql.Connection, note_id: int
                         ) -> dict[str, Union[int, str, datetime.datetime]]:
    """
    Fetch the one particular note.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param note_id: note id
    :type note_id: int

    :return: data of the note
    :rtype: dict[str, Union[int, str, datetime.datetime]]
    """

    query = """
        SELECT 
            `notes`.*, 
            `note_rubrics`.title AS `rubric`
        FROM
            `notes`
                LEFT JOIN
            `note_rubrics` ON `notes`.`rubric_id` = `note_rubrics`.`id`
        WHERE
            `notes`.`id` = %(note_id)s
        ;
    """
    params = {
        'note_id': note_id
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query, params)
        note = await cursor.fetchone()

    return note


# # # ------------------------- Users


@check_record_in_db
async def fetch_one_user(connection: aiomysql.Connection,
                         *args: Any,
                         user_id: Optional[int] = None, login: Optional[str] = None, password: Optional[str] = None,
                         ) -> dict[str, Union[int, str]]:
    """
    Fetch the user by keyword argument(s).

    Will raise an error if no one keyword argument was passed.
    If were passed few arguments - all will be considered.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :keyword user_id: user id
    :type user_id: int
    :keyword login: login
    :type login: str
    :keyword password: password
    :type password: str

    :return: data of the user
    :rtype: dict[str, Union[int, str]]

    :raises TypeError: raised if no one keyword argument was passed
    """

    if not (user_id or login or password):
        message = "fetch_one_user() missing (at least) 1 required keyword argument: ('user_id', 'login', 'password')"
        raise TypeError(message)

    query_template = """
        SELECT 
            *
        FROM
            `users`
        WHERE
            1 = 1
            {% if user_id %}
                AND `id` = {{ user_id }}
            {% endif %}
            {% if login %}
                AND `login` = {{ login }}
            {% endif %}    
            {% if password %}
                AND `password` = {{ password }}
            {% endif %}
        ;    
    """
    params = {
        'user_id': user_id,
        'login': login,
        'password': password
    }

    query, bound_params = jinja_sql.prepare_query(query_template, params)

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(query, bound_params)
        user = await cursor.fetchone()

    return user


# # ------------------------- CREATE QUERIES
# # # ------------------------- Posts


async def insert_post_rubric(connection: aiomysql.Connection, post_rubric: validators.PostRubricCreation) -> None:
    """
    Insert new post rubric.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param post_rubric: validated data of the post rubric
    :type post_rubric: validators.PostRubricCreation

    :return: None
    :rtype: None
    """
    query = 'INSERT INTO `post_rubrics` (`title`, `user_id`) VALUES (%(title)s, %(user_id)s);'
    params = post_rubric.dict(by_alias=True)

    await execute_query(connection, query, params)


async def insert_post(connection: aiomysql.Connection, post: validators.PostCreation) -> None:
    """
    Insert new post.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param post: validated data of the post
    :type post: validators.PostCreation

    :return: None
    :rtype: None
    """

    query = """
        INSERT INTO `posts` (`title`, `content`, `user_id`, `rubric_id`) 
        VALUES (%(title)s, %(content)s, %(user_id)s, %(rubric_id)s)
        ;
    """
    params = post.dict(by_alias=True)

    await execute_query(connection, query, params)


# # # ------------------------- Notes

async def insert_note_rubric(connection: aiomysql.Connection, note_rubric: validators.NoteRubricCreation) -> None:
    """
    Insert new note rubric.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param note_rubric: validated data of the note rubric
    :type note_rubric: validators.NoteRubricCreation

    :return: None
    :rtype: None
    """

    query = 'INSERT INTO `note_rubrics` (`title`, `user_id`) VALUES (%(title)s, %(user_id)s);'
    params = note_rubric.dict(by_alias=True)

    await execute_query(connection, query, params)


async def insert_note(connection: aiomysql.Connection, note: validators.NoteCreation) -> None:
    """
    Insert new note.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param note: validated data of the note
    :type note: validators.NoteCreation

    :return: None
    :rtype: None
    """

    query = """
        INSERT INTO `notes` (`content`, `rubric_id`, `user_id`) 
        VALUES (%(content)s, %(rubric_id)s, %(user_id)s)
        ;
    """
    params = note.dict(by_alias=True)

    await execute_query(connection, query, params)


# # # ------------------------- Users


async def insert_user(connection: aiomysql.Connection, user: validators.UserCreation) -> None:
    """
    Insert new user.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param user: validated data of the user
    :type user: validators.UserCreation

    :return: None
    :rtype: None
    """

    query = """
        INSERT INTO `users` (`login`, `password`) 
        VALUES (%(login)s, %(password)s)
        ;
    """
    params = user.dict(by_alias=True)

    await execute_query(connection, query, params)


# # ------------------------- UPDATE QUERIES


# # # ------------------------- Posts


async def update_post_rubric(connection: aiomysql.Connection,
                             post_rubric_id: int, post_rubric: validators.PostRubricEditing
                             ) -> None:
    """
    Update the post rubric.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param post_rubric_id: post rubric id
    :type post_rubric_id: int
    :param post_rubric: validated data of the post rubric
    :type post_rubric: validators.PostRubricEditing

    :return: None
    :rtype: None
    """

    query = """
        UPDATE `post_rubrics` 
        SET 
            `title` = %(title)s
        WHERE
            `id` = %(post_rubric_id)s;
    """
    params = post_rubric.dict(by_alias=True)
    params['post_rubric_id'] = post_rubric_id

    await execute_query(connection, query, params)


async def update_post(connection: aiomysql.Connection, post_id: int, post: validators.PostEditing) -> None:
    """
    Update the post.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param post_id: post id
    :type post_id: int
    :param post: validated data of the post
    :type post: validators.PostCreation

    :return: None
    :rtype: None
    """

    query = """
        UPDATE `posts` 
        SET 
            `title` = %(title)s,
            `content` = %(content)s,
            `rubric_id` = %(rubric_id)s
        WHERE
            `id` = %(post_id)s;
    """
    params = post.dict(by_alias=True)
    params['post_id'] = post_id

    await execute_query(connection, query, params)


# # # ------------------------- Notes


async def update_note_rubric(connection: aiomysql.Connection,
                             note_rubric_id: int, note_rubric: validators.NoteRubricEditing
                             ) -> None:
    """
    Update the note rubric.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param note_rubric_id: note rubric id
    :type note_rubric_id: int
    :param note_rubric: validated data of the note rubric
    :type note_rubric: validators.NoteRubricEditing

    :return: None
    :rtype: None
    """

    query = """
        UPDATE `note_rubrics` 
        SET 
            `title` = %(title)s
        WHERE
            `id` = %(note_rubric_id)s;
    """
    params = note_rubric.dict(by_alias=True)
    params['note_rubric_id'] = note_rubric_id

    await execute_query(connection, query, params)


async def update_note(connection: aiomysql.Connection, note_id: int, note: validators.NoteEditing) -> None:
    """
    Update the note.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param note_id: note id
    :type note_id: int
    :param note: validated data of the note
    :type note: validators.NoteEditing

    :return: None
    :rtype: None
    """

    query = """
        UPDATE `notes` 
        SET 
            `content` = %(content)s,
            `note_rubric_id` = %(rubric_id)s
        WHERE
            `id` = %(note_id)s;
    """
    params = note.dict(by_alias=True)
    params['note_id'] = note_id

    await execute_query(connection, query, params)


# # # ------------------------- Users


# async def update_user(connection: aiomysql.Connection, user_id: int, user: validators.UserCreation) -> None:
#     """
#     Update the user.
#
#     :param connection: db connection
#     :type connection: aiomysql.Connection
#     :param user_id: user id
#     :type user_id: int
#     :param user: validated data of the user
#     :type user: validators.UserCreation
#
#     :return: None
#     :rtype: None
#     """
#
#     query = """
#         UPDATE `users`
#         SET
#             `login` = %(login)s,
#             `password` = %(password)s
#         WHERE
#             `id` = %(user_id)s;
#     """
#     params = user.dict(by_alias=True)
#     params['user_id'] = user_id
#
#     await execute_query(connection, query, params)


# # ------------------------- DELETE QUERIES


# # # Posts


async def delete_post_rubric(connection: aiomysql.Connection, post_rubric_id: int) -> None:
    """
    Delete the post rubric.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param post_rubric_id: post rubric id
    :type post_rubric_id: int

    :return: None
    :rtype: None
    """

    query = """
        DELETE FROM `post_rubrics` 
        WHERE
            `id` = %(post_rubric_id)s;
    """
    params = {
        'post_rubric_id': post_rubric_id
    }

    await execute_query(connection, query, params)


async def delete_post(connection: aiomysql.Connection, post_id: int,) -> None:
    """
    Delete the post.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param post_id: post id
    :type post_id: int

    :return: None
    :rtype: None
    """

    query = """
        DELETE FROM `posts` 
        WHERE
            `id` = %(post_id)s;
    """
    params = {
        'post_id': post_id
    }

    await execute_query(connection, query, params)


# # # Notes


async def delete_note_rubric(connection: aiomysql.Connection, note_rubric_id: int) -> None:
    """
    Delete the note rubric.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param note_rubric_id: note rubric id
    :type note_rubric_id: int

    :return: None
    :rtype: None
    """

    query = """
        DELETE FROM `note_rubrics` 
        WHERE
            `id` = %(note_rubric_id)s;
    """
    params = {
        'note_rubric_id': note_rubric_id
    }

    await execute_query(connection, query, params)


async def delete_note(connection: aiomysql.Connection, note_id: int,) -> None:
    """
    Delete the note.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param note_id: note id
    :type note_id: int

    :return: None
    :rtype: None
    """

    query = """
        DELETE FROM `notes` 
        WHERE
            `id` = %(note_id)s;
    """
    params = {
        'note_id': note_id
    }

    await execute_query(connection, query, params)


# # # Users


async def delete_user(connection: aiomysql.Connection, user_id: int) -> None:
    """
    Delete the user.

    :param connection: db connection
    :type connection: aiomysql.Connection
    :param user_id: user id
    :type user_id: int

    :return: None
    :rtype: None
    """

    query = """
        DELETE FROM `users` 
        WHERE
            `id` = %(user_id)s;
    """
    params = {
        'user_id': user_id
    }

    await execute_query(connection, query, params)


# ------------------------- Admin manipulations
