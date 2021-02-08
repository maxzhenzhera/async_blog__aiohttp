"""
Contains functions that execute CRUD operations with db.


Classes {errors}:
    class RecordNotFoundError(Exception):
    = raised when record in the DB is not found
    --------------------------------------------------------------------------------------------------------------------
Functions:
    async def execute_query(connection: aiomysql.Connection, query: str, params: dict, *args, **kwargs) -> None:
    = execute query (might be used for insert, update, delete actions)
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_rows_quantity(connection: aiomysql.Connection, entity: str = 'posts', *args, **kwargs) -> int:
    = fetch rows quantity one of the entity (posts, notes)
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_post_rubrics(connection: aiomysql.Connection,*args, **kwargs
        ) -> list[dict[str, Union[int, str]]]:
    = fetch all post rubrics
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_posts(connection: aiomysql.Connection, rubric_id: Optional[int] = None,
        search_word: Optional[str] = None, page_number: int = 1, posts_quantity: int = DEFAULT_POSTS_ON_PAGE, *args,
        user_id: Optional[int] = None, **kwargs ) -> list[dict[str, Union[int, str, datetime.datetime]]]:
    = fetch all posts (by default return posts for the first page, might fetch posts by particular page)
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_one_post(connection: aiomysql.Connection, post_id: int, *args, **kwargs
        ) -> dict[str, Union[int, str, datetime.datetime]]:
    = fetch one post by id
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_one_random_post(connection: aiomysql.Connection, *args, **kwargs
        ) -> dict[str, Union[int, str, datetime.datetime]]:
    = fetch one random post
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_note_rubrics(connection: aiomysql.Connection, user_id: int, *args, **kwargs
        ) -> list[dict[str, Union[int, str]]]:
    = fetch all note rubrics
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_notes(connection: aiomysql.Connection, user_id: int, rubric_id: int = None,
        search_word: str = None, page_number: int = 1, notes_quantity: int = DEFAULT_NOTES_ON_PAGE, *args, **kwargs
        ) -> list[dict[str, Union[int, str, datetime.datetime]]]:
    = fetch all notes (by default return notes for the first page, might fetch notes by particular page)
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_one_note(connection: aiomysql.Connection, note_id: int,*args, **kwargs
        ) -> dict[str, Union[int, str, datetime.datetime]]:
    = fetch one note by id
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_one_user(connection: aiomysql.Connection, *args,
        user_id: int = None, login: str = None, password: str = None, **kwargs) -> dict[str, Union[int, str]]:
    = fetch the user by keyword arguments
    --------------------------------------------------------------------------------------------------------------------
    async def insert_post_rubric(connection: aiomysql.Connection, user_id: int, title: str,*args, **kwargs) -> None:
    = insert new post rubric
    --------------------------------------------------------------------------------------------------------------------
    async def insert_post(connection: aiomysql.Connection, user_id: int, title: str, content: str, rubric_id: int,
        *args, **kwargs) -> None:
    = insert new post
    --------------------------------------------------------------------------------------------------------------------
    async def insert_note_rubric(connection: aiomysql.Connection,user_id: int, title: str,*args, **kwargs) -> None:
    = insert new note rubric
    --------------------------------------------------------------------------------------------------------------------
    async def insert_note(connection: aiomysql.Connection, user_id: int, title: str, content: str,
        rubric_id: Optional[int] = None, *args, **kwargs ) -> None:
    = insert new note
    --------------------------------------------------------------------------------------------------------------------
    async def insert_user(connection: aiomysql.Connection,login: str, password: str,*args, **kwargs) -> None:
    = insert new user (register)
    --------------------------------------------------------------------------------------------------------------------
    async def update_post_rubric(connection: aiomysql.Connection,post_rubric_id: int, title: str,
        *args, **kwargs) -> None:
    = update post rubric
    --------------------------------------------------------------------------------------------------------------------
    async def update_post(connection: aiomysql.Connection,post_id: int, title: str, content: str, rubric_id: int,
        *args, **kwargs) -> None:
    = update post
    --------------------------------------------------------------------------------------------------------------------
    async def update_note_rubric(connection: aiomysql.Connection,note_rubric_id: int, title: str,
        *args, **kwargs) -> None:
    = update note rubric
    --------------------------------------------------------------------------------------------------------------------
    async def update_note(connection: aiomysql.Connection, note_id: int, content: str, rubric_id: Optional[int] = None,
        *args, **kwargs ) -> None:
    = update note
    --------------------------------------------------------------------------------------------------------------------
    async def update_user(connection: aiomysql.Connection,user_id: int, login: str, password: str,
        *args, **kwargs) -> None:
    = update user
    --------------------------------------------------------------------------------------------------------------------
    async def delete_post_rubric(connection: aiomysql.Connection,post_rubric_id: int,*args, **kwargs) -> None:
    = delete post rubric
    --------------------------------------------------------------------------------------------------------------------
    async def delete_post(connection: aiomysql.Connection,post_id: int,*args, **kwargs) -> None:
    = delete post
    --------------------------------------------------------------------------------------------------------------------
    async def delete_note_rubric(connection: aiomysql.Connection,note_rubric_id: int,*args, **kwargs) -> None:
    = delete note rubric
    --------------------------------------------------------------------------------------------------------------------
    async def delete_note(connection: aiomysql.Connection,note_id: int,*args, **kwargs) -> None:
    = delete note
    --------------------------------------------------------------------------------------------------------------------
    async def delete_user(connection: aiomysql.Connection,user_id: int,*args, **kwargs) -> None:
    = delete user
    --------------------------------------------------------------------------------------------------------------------
    async def make_user_moderator(connection: aiomysql.Connection,user_id: int,*args, **kwargs) -> None:
    = give user (by id) `moderator` grant
    --------------------------------------------------------------------------------------------------------------------
    async def make_moderator_simple_user(connection: aiomysql.Connection, user_id: int, *args, **kwargs ) -> None:
    = take away `moderator` grant from user (by id)
    --------------------------------------------------------------------------------------------------------------------
Vars:
    jinja_sql: JinjaSql | engine for sql templating
"""

import datetime
import random
from typing import (
    Optional,
    Union
)

import aiomysql
from jinjasql import JinjaSql

from core.settings import (
    DEFAULT_POSTS_ON_PAGE,
    DEFAULT_NOTES_ON_PAGE
)

# template engine for sql on Jinja basis
jinja_sql = JinjaSql(param_style='pyformat')


# internal db errors
class RecordNotFoundError(Exception):
    """ Raised when record in the DB is not found """


# ------------------------- HELP FUNCTIONS (SHORTCUT)


async def execute_query(connection: aiomysql.Connection,
                        query: str, params: dict,
                        *args, **kwargs
                        ) -> None:
    """ Execute query (might be used for insert, update, delete actions) """
    async with connection.cursor() as cursor:
        cursor.execute(query, params)


# ------------------------- CRUD OPERATIONS


# # ------------------------- AGGREGATE QUERIES

async def fetch_rows_quantity(connection: aiomysql.Connection,
                              entity: str,
                              *args, **kwargs
                              ) -> int:
    """
    Fetch all post rubrics for page

    Keyword `entity`:
        type: str
        possible arguments:
            - 'posts'
            - 'notes'

    Raise:
        ValueError  - when incorrect type of `entity` argument
        TypeError   - when incorrect value of `entity` argument (value must be in possible arguments list)
    """

    posts_query = 'SELECT COUNT(*) FROM `posts`;'
    notes_query = 'SELECT COUNT(*) FROM `notes`;'

    async with connection.cursor() as cursor:
        if entity == 'posts':
            query = posts_query
        elif entity == 'notes':
            query = notes_query
        else:
            if isinstance(entity, str):
                raise ValueError()
            else:
                raise TypeError()

        await cursor.execute(
            query
        )

        query_result = await cursor.fetchone()
        quantity_of_rows = int(query_result[0])

        return quantity_of_rows

# # ------------------------- READ QUERIES


# # # ------------------------- Posts


async def fetch_all_post_rubrics(connection: aiomysql.Connection,
                                 *args, **kwargs
                                 ) -> list[dict[str, Union[int, str]]]:
    """  Fetch all post rubrics for page """
    query = 'SELECT * FROM `post_rubrics`;'

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            query
        )
        post_rubrics = await cursor.fetchall()
        return post_rubrics


async def fetch_all_posts(connection: aiomysql.Connection,
                          rubric_id: Optional[int] = None, search_word: Optional[str] = None,
                          page_number: int = 1, rows_quantity: int = DEFAULT_POSTS_ON_PAGE,
                          *args,
                          user_id: Optional[int] = None,
                          **kwargs
                          ) -> list[dict[str, Union[int, str, datetime.datetime]]]:
    """ Fetch all posts (considering extra arguments) """
    query_template = """
        SELECT
            `posts`.*,
            `post_rubrics`.`title` AS `rubric`
        FROM
            `posts`
                INNER JOIN
            `post_rubrics` ON `posts`.`post_rubric_id` = `post_rubrics`.`id`
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
        LIMIT {{ offset }}, {{ posts_quantity }};
    """
    params = {
        'rubric_id': rubric_id,
        'search_word': search_word,
        'offset': (page_number - 1) * rows_quantity,
        'posts_quantity': rows_quantity,
        'user_id': user_id
    }
    query, params = jinja_sql.prepare_query(query_template, params)

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            query,
            params
        )
        posts = await cursor.fetchall()
        return posts


async def fetch_one_post(connection: aiomysql.Connection,
                         post_id: int,
                         *args, **kwargs
                         ) -> dict[str, Union[int, str, datetime.datetime]]:
    """  Fetch the one particular post """
    query = """
        SELECT
            `posts`.*,
            `post_rubrics`.`title` AS `rubric`
        FROM
            `posts`
                INNER JOIN
            `post_rubrics` ON `posts`.`post_rubric_id` = `post_rubrics`.`id`
        WHERE
            `posts`.`id` = %(post_id)s;
    """
    params = {
        'post_id': post_id
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            query,
            params
        )
        post = await cursor.fetchone()

        if post:
            return post
        else:
            raise RecordNotFoundError


async def fetch_one_random_post(connection: aiomysql.Connection,
                                *args, **kwargs
                                ) -> dict[str, Union[int, str, datetime.datetime]]:
    """  Fetch an one random post """
    query = """
        SELECT
            `posts`.*,
            `post_rubrics`.`title` AS `rubric`
        FROM
            `posts`
                INNER JOIN
            `post_rubrics` ON `posts`.`post_rubric_id` = `post_rubrics`.`id`
        ORDER BY %(order_key)s LIMIT 1;
    """
    params = {
        'order_key': random.random()
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            query,
            params
        )
        post = await cursor.fetchone()
        return post


# # # ------------------------- Notes


async def fetch_all_note_rubrics(connection: aiomysql.Connection,
                                 user_id: int,
                                 *args, **kwargs
                                 ) -> list[dict[str, Union[int, str]]]:
    """ Fetch all notes by rubric """
    query = 'SELECT * FROM `note_rubrics` WHERE `user_id` = %(user_id)s ORDER BY `title`;'
    params = {
        'user_id': user_id
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            query,
            params
        )
        note_rubrics = await cursor.fetchall()
        return note_rubrics


async def fetch_all_notes(connection: aiomysql.Connection,
                          user_id: int,
                          rubric_id: int = None, search_word: str = None,
                          page_number: int = 1, notes_quantity: int = DEFAULT_NOTES_ON_PAGE,
                          *args, **kwargs
                          ) -> list[dict[str, Union[int, str, datetime.datetime]]]:
    """ Fetch all notes (considering extra arguments) """
    query_template = """
        SELECT 
            `notes`.*, 
            `note_rubrics`.title AS `rubric`
        FROM
            `notes`
                INNER JOIN
            `note_rubrics` ON `notes`.`id` = `note_rubrics`.`id`
        WHERE
            `notes`.`user_id` = %(user_id)s
            {% if rubric_id %}
                AND `note_rubric_id` = {{ rubric_id }}
            {% endif %}
            {% if search_word %}
                AND MATCH (`notes`.`content`) AGAINST ({{ search_word }})
            {% endif %}
        LIMIT {{ offset }}, {{ notes_quantity }}; 
    """
    params = {
        'user_id': user_id,
        'rubric_id': rubric_id,
        'search_word': search_word,
        'offset': (page_number - 1) * notes_quantity,
        'notes_quantity': notes_quantity
    }
    query, params = jinja_sql.prepare_query(query_template, params)

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            query,
            params
        )
        notes = await cursor.fetchall()
        return notes


async def fetch_one_note(connection: aiomysql.Connection,
                         note_id: int,
                         *args, **kwargs
                         ) -> dict[str, Union[int, str, datetime.datetime]]:
    """  Fetch the one particular note """
    query = """
        SELECT 
            `notes`.*, 
            `note_rubrics`.title AS `rubric`
        FROM
            `notes`
                INNER JOIN
            `note_rubrics` ON `notes`.`id` = `note_rubrics`.`id`
        WHERE
            `notes`.`id` = %(note_id)s
    """
    params = {
        'note_id': note_id
    }

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            query,
            params
        )
        note = await cursor.fetchone()

        if note:
            return note
        else:
            raise RecordNotFoundError


# # # ------------------------- Users


async def fetch_one_user(connection: aiomysql.Connection,
                         *args,
                         user_id: int = None, login: str = None, password: str = None,
                         **kwargs
                         ) -> dict[str, Union[int, str]]:
    """
    Fetch the user by keyword arguments.

    If no one keyword argument was passed -> raise an error.
    If were passed few arguments - all will be considered.

    Raise:
        TypeError               (when no one keyword argument was passed)
        RecordNotFoundError     (when a record was not found)
    """

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

    if not (user_id or login or password):
        message = "fetch_one_user() missing (at least) 1 required keyword argument: ('user_id', 'login', 'password')"
        raise TypeError(message)

    query, params = jinja_sql.prepare_query(query_template, params)

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            query,
            params
        )
        user = await cursor.fetchone()

        if user:
            return user
        else:
            raise RecordNotFoundError


# # ------------------------- CREATE QUERIES
# # # ------------------------- Posts


async def insert_post_rubric(connection: aiomysql.Connection,
                             user_id: int, title: str,
                             *args, **kwargs) -> None:
    """ Insert new post rubric """
    query = 'INSERT INTO `post_rubrics` (`title`, `user_id`) VALUES (%(title)s, %(user_id)s);'
    params = {
        'title': title,
        'user_id': user_id
    }

    await execute_query(connection, query, params)


async def insert_post(connection: aiomysql.Connection,
                      user_id: int, title: str, content: str, rubric_id: int,
                      *args, **kwargs
                      ) -> None:
    """ Insert new post """
    query = """
        INSERT INTO `posts` (`title`, `content`, `user_id`, `post_rubric_id`) 
        VALUES (%(title)s, %(content)s, %(user_id)s, %(post_rubric_id)s);'
    """
    params = {
        'title': title,
        'content': content,
        'user_id': user_id,
        'rubric_id': rubric_id
    }

    await execute_query(connection, query, params)


# # # ------------------------- Notes

async def insert_note_rubric(connection: aiomysql.Connection,
                             user_id: int, title: str,
                             *args, **kwargs
                             ) -> None:
    """ Insert new note rubric """
    query = 'INSERT INTO `note_rubrics` (`title`, `user_id`) VALUES (%(title)s, %(user_id)s);'
    params = {
        'title': title,
        'user_id': user_id
    }

    await execute_query(connection, query, params)


async def insert_note(connection: aiomysql.Connection,
                      user_id: int, title: str, content: str, rubric_id: Optional[int] = None,
                      *args, **kwargs
                      ) -> None:
    """ Insert new note """
    query = """
        INSERT INTO `notes` (`title`, `content`, `note_rubric_id`, `user_id`) 
        VALUES (%(title)s, %(content)s, %(note_rubric_id)s, %(user_id)s);
    """
    params = {
        'title': title,
        'content': content,
        'note_rubric_id': rubric_id,
        'user_id': user_id
    }

    await execute_query(connection, query, params)


# # # ------------------------- Users


async def insert_user(connection: aiomysql.Connection,
                      login: str, password: str,
                      *args, **kwargs
                      ) -> None:
    """ Insert new user """
    query = """
        INSERT INTO `users` (`login`, `password`, `is_admin`) 
        VALUES (%(login)s, %(password)s, %(is_admin)s);
    """
    params = {
        'login': login,
        'password': password
    }

    await execute_query(connection, query, params)


# # ------------------------- UPDATE QUERIES


# # # ------------------------- Posts


async def update_post_rubric(connection: aiomysql.Connection,
                             post_rubric_id: int, title: str,
                             *args, **kwargs
                             ) -> None:
    """ Update the post rubric """
    query = """
        UPDATE `post_rubrics` 
        SET 
            `title` = %(title)s
        WHERE
            `id` = %(post_rubric_id)s;
    """
    params = {
        'title': title,
        'post_rubric_id': post_rubric_id
    }

    await execute_query(connection, query, params)


async def update_post(connection: aiomysql.Connection,
                      post_id: int, title: str, content: str, rubric_id: int,
                      *args, **kwargs
                      ) -> None:
    """ Update the post """
    query = """
        UPDATE `posts` 
        SET 
            `title` = %(title)s,
            `content` = %(content)s,
            `post_rubric_id` = %(rubric_id)s
        WHERE
            `id` = %(post_id)s;
    """
    params = {
        'title': title,
        'content': content,
        'rubric_id': rubric_id,
        'post_id': post_id
    }

    await execute_query(connection, query, params)


# # # ------------------------- Notes


async def update_note_rubric(connection: aiomysql.Connection,
                             note_rubric_id: int, title: str,
                             *args, **kwargs
                             ) -> None:
    """ Update the note rubric """
    query = """
        UPDATE `note_rubrics` 
        SET 
            `title` = %(title)s
        WHERE
            `id` = %(note_rubric_id)s;
    """
    params = {
        'title': title,
        'note_rubric_id': note_rubric_id
    }

    await execute_query(connection, query, params)


async def update_note(connection: aiomysql.Connection,
                      note_id: int, content: str, rubric_id: Optional[int] = None,
                      *args, **kwargs
                      ) -> None:
    """ Update the note """
    query = """
        UPDATE `notes` 
        SET 
            `content` = %(content)s,
            `note_rubric_id` = %(rubric_id)s
        WHERE
            `id` = %(note_id)s;
    """
    params = {
        'content': content,
        'rubric_id': rubric_id,
        'note_id': note_id
    }

    await execute_query(connection, query, params)


# # # ------------------------- Users


async def update_user(connection: aiomysql.Connection,
                      user_id: int, login: str, password: str,
                      *args, **kwargs
                      ) -> None:
    """ Update the user """
    query = """
        UPDATE `users` 
        SET 
            `login` = %(login)s,
            `password` = %(password)s
        WHERE
            `id` = %(user_id)s;
    """
    params = {
        'login': login,
        'password': password,
        'user_id': user_id
    }

    await execute_query(connection, query, params)


# # ------------------------- DELETE QUERIES


# # # Posts


async def delete_post_rubric(connection: aiomysql.Connection,
                             post_rubric_id: int,
                             *args, **kwargs
                             ) -> None:
    """ Delete the post rubric """
    query = """
        DELETE FROM `post_rubrics` 
        WHERE
            `id` = %(post_rubric_id)s;
    """
    params = {
        'post_rubric_id': post_rubric_id
    }

    await execute_query(connection, query, params)


async def delete_post(connection: aiomysql.Connection,
                      post_id: int,
                      *args, **kwargs
                      ) -> None:
    """ Delete the post """
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


async def delete_note_rubric(connection: aiomysql.Connection,
                             note_rubric_id: int,
                             *args, **kwargs
                             ) -> None:
    """ Delete the note rubric """
    query = """
        DELETE FROM `note_rubrics` 
        WHERE
            `id` = %(note_rubric_id)s;
    """
    params = {
        'note_rubric_id': note_rubric_id
    }

    await execute_query(connection, query, params)


async def delete_note(connection: aiomysql.Connection,
                      note_id: int,
                      *args, **kwargs
                      ) -> None:
    """ Delete the note """
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


async def delete_user(connection: aiomysql.Connection,
                      user_id: int,
                      *args, **kwargs
                      ) -> None:
    """ Delete the user """
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


async def make_user_moderator(connection: aiomysql.Connection,
                              user_id: int,
                              *args, **kwargs
                              ) -> None:
    """ Add the user `moderator` grant """
    query = """
        UPDATE `users` 
        SET 
            `is_moderator` = 1
        WHERE
            `id` = %(user_id)s;
    """
    params = {
        'user_id': user_id
    }

    await execute_query(connection, query, params)


async def make_moderator_simple_user(connection: aiomysql.Connection,
                                     user_id: int,
                                     *args, **kwargs
                                     ) -> None:
    """ Take away the user `moderator` grant """
    query = """
        UPDATE `users` 
        SET 
            `is_moderator` = 0
        WHERE
            `id` = %(user_id)s;
    """
    params = {
        'user_id': user_id
    }

    await execute_query(connection, query, params)
