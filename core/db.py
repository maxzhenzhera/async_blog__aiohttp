"""
Contains classes that implement the database objects. `Database` and `TableName` contain only sql queries.

# # For future = sql queries will be used in some `Executor` class
# # that get connection in __init__ and then use it in methods

Classes:
    class Database | Contains queries that create/drop database, database`s user
    --------------------------------------------------------------------------------------------------------------------
    class TableUsers        | classes like `TableName` implement one entity type:
    ------------------------- each class contains queries that create/drop table.
    class TablePostRubrics  |
    -------------------------
    class TablePosts        |
    -------------------------
    class TableNoteRubrics  |
    -------------------------
    class TableNotes        |
    --------------------------------------------------------------------------------------------------------------------
Functions:
    async def init_mysql | (app: aiohttp.web.Application) -> None | init mysql connection (create pool)
    --------------------------------------------------------------------------------------------------------------------
    async def close_mysql | (app: aiohttp.web.Application) | close mysql connection (close pool)
    --------------------------------------------------------------------------------------------------------------------
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    FETCH DATA
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_post_rubrics | (connection: aiomysql.Connection, *args
    ) -> List[Dict[str, Union[int, str]]] | fetch all post rubrics
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_posts_quantity | (connection: aiomysql.Connection, *args
    ) -> int | count quantity of posts
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_one_post | (connection: aiomysql.Connection, post_id: int, *args
    ) -> Dict[str, Union[int, str, datetime.datetime]] | fetch the one particular post
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_one_random_post | (connection: aiomysql.Connection, *args
    ) -> Dict[str, Union[int, str, datetime.datetime]] | fetch an one random post
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_posts | (connection: aiomysql.Connection, *args
    ) -> List[Dict[str, Union[int, str, datetime.datetime]]] | fetch all posts
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_posts_for_page | (connection: aiomysql.Connection, *args, page: int = 1, rows_quantity: int = 10
    ) -> List[Dict[str, Union[int, str, datetime.datetime]]] | fetch posts with limited quantity (for one page)
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_posts_by_rubric | (connection: aiomysql.Connection, rubric_id: int, *args
    ) -> List[Dict[str, Union[int, str, datetime.datetime]]] | fetch all posts sorted by rubric
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_posts_by_rubric_for_page | (connection: aiomysql.Connection, rubric_id: int, *args,
    page: int = 1, rows_quantity: int = 10
    ) -> List[Dict[str, Union[int, str, datetime.datetime]]] | fetch posts sorted by rubric with limited quantity
    (for one page)
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_note_rubrics | (connection: aiomysql.Connection, user_id: int
    ) -> List[Dict[str, Union[int, str]]] | fetch note rubrics
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_notes | (connection: aiomysql.Connection, user_id: int
    ) -> List[Dict[str, Union[int, str, datetime.datetime]]] | fetch notes
    --------------------------------------------------------------------------------------------------------------------
    async def fetch_all_notes_by_rubric | (connection: aiomysql.Connection, user_id: int, rubric_id: int
    ) -> List[Dict[str, Union[int, str, datetime.datetime]]] | fetch notes sorted by rubric
    --------------------------------------------------------------------------------------------------------------------
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    INSERT DATA
    --------------------------------------------------------------------------------------------------------------------
        ...
    --------------------------------------------------------------------------------------------------------------------
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    UPDATE DATA
    --------------------------------------------------------------------------------------------------------------------
        ...
    --------------------------------------------------------------------------------------------------------------------
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    DELETE DATA
    --------------------------------------------------------------------------------------------------------------------
        ...
    --------------------------------------------------------------------------------------------------------------------
Vars:
    tables: tuple | contains all database tables in order (ParentTable, ChildTable)
    --------------------------------------------------------------------------------------------------------------------
"""

import asyncio
import datetime
import random
from typing import (
    List,
    Dict,
    Union
)

import aiohttp.web
import aiomysql
from loguru import logger


class Database:
    """ Implement app database """

    # DB
    create_database = (
        "DROP DATABASE IF EXISTS {db_name};                                     "
        "CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET utf8;    "
    )
    drop_database = "DROP SCHEMA IF EXISTS {db_name}"

    # DB user
    create_user = (
        "DROP USER IF EXISTS {user_name}@{host};                                       "
        "CREATE USER IF NOT EXISTS {user_name}@{host} IDENTIFIED BY '{user_password}'; "
        "GRANT ALL PRIVILEGES ON {db_name}.* TO {user_name}@{host};                    "
    )
    drop_user = "DROP USER IF EXISTS {user_name};"


class TableUsers:
    """ Implement `users` table """

    create_table = (
        "DROP TABLE IF EXISTS `users`;          "
        "CREATE TABLE IF NOT EXISTS `users` (   "
        "    `id` INT NOT NULL AUTO_INCREMENT,  "
        "    `login` VARCHAR(255) NOT NULL,     "
        "    `password` VARCHAR(255) NOT NULL,  "
        "    `is_admin` TINYINT NOT NULL,       "
        "    PRIMARY KEY (`id`)                 "
        ")  ENGINE=INNODB;                      "
    )
    drop_table = "DROP TABLE IF EXISTS `users` ;"


class TablePostRubrics:
    """ Implement `post_rubrics` table """

    create_table = (
        "DROP TABLE IF EXISTS `post_rubrics`;           "
        "CREATE TABLE IF NOT EXISTS `post_rubrics` (    "
        "    `id` INT NOT NULL AUTO_INCREMENT,          "
        "    `title` VARCHAR(255) NOT NULL,             "
        "    `user_id` INT NULL,                        "
        "    PRIMARY KEY (`id`),                        "
        "    FOREIGN KEY (`user_id`)                    "
        "        REFERENCES `users` (`id`)              "
        "        ON DELETE SET NULL ON UPDATE NO ACTION "
        ")  ENGINE=INNODB;                              "
    )
    drop_table = "DROP TABLE IF EXISTS `post_rubrics`;"


class TablePosts:
    """ Implement `posts` table """

    create_table = (
        "DROP TABLE IF EXISTS `posts`;                                                              "
        "CREATE TABLE IF NOT EXISTS `posts` (                                                       "
        "    `id` INT NOT NULL AUTO_INCREMENT,                                                      "
        "    `title` VARCHAR(255) NOT NULL,                                                         "
        "    `content` TEXT NOT NULL,                                                               "
        "    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,                            "
        "    `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, "
        "    `user_id` INT NULL,                                                                    "
        "    `post_rubric_id` INT NULL,                                                             "
        "    PRIMARY KEY (`id`),                                                                    "
        "    FULLTEXT ( `title` , `content` ),                                                      "
        "    FOREIGN KEY (`user_id`)                                                                " 
        "        REFERENCES `users` (`id`)                                                          "
        "        ON DELETE SET NULL ON UPDATE NO ACTION,                                            "    
        "    FOREIGN KEY (`post_rubric_id`)                                                         "
        "        REFERENCES `post_rubrics` (`id`)                                                   "
        "        ON DELETE SET NULL ON UPDATE NO ACTION                                             "
        ")  ENGINE=INNODB;                                                                          "
    )
    drop_table = "DROP TABLE IF EXISTS `posts`;"


class TableNoteRubrics:
    """ Implement `note_rubrics` table """

    create_table = (
        "DROP TABLE IF EXISTS `note_rubrics`;           "
        "CREATE TABLE IF NOT EXISTS `note_rubrics` (    "
        "    `id` INT NOT NULL AUTO_INCREMENT,          "
        "    `title` VARCHAR(255) NOT NULL,             "
        "    `user_id` INT NOT NULL,                    "
        "    PRIMARY KEY (`id`),                        "
        "    FOREIGN KEY (`user_id`)                    "
        "        REFERENCES `users` (`id`)              "
        "        ON DELETE CASCADE ON UPDATE NO ACTION  "
        ")  ENGINE=INNODB;                              "
    )
    drop_table = (
        "DROP TABLE IF EXISTS `note_rubrics`;"
    )


class TableNotes:
    """ Implement `notes` table """

    create_table = (
        "DROP TABLE IF EXISTS `notes`;                                                              "
        "CREATE TABLE IF NOT EXISTS `notes` (                                                       "
        "    `id` INT NOT NULL AUTO_INCREMENT,                                                      "
        "    `content` VARCHAR(255) NOT NULL,                                                       "
        "    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,                            "
        "    `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, "
        "    `note_rubric_id` INT NULL,                                                             "
        "    `user_id` INT NOT NULL,                                                                "
        "    PRIMARY KEY (`id`),                                                                    "
        "    FOREIGN KEY (`note_rubric_id`)                                                         "
        "        REFERENCES `note_rubrics` (`id`)                                                   "
        "        ON DELETE CASCADE ON UPDATE NO ACTION,                                             "
        "    FOREIGN KEY (`user_id`)                                                                "
        "        REFERENCES `users` (`id`)                                                          "
        "        ON DELETE CASCADE ON UPDATE NO ACTION                                              "
        ")  ENGINE=INNODB;                                                                          "
    )
    drop_table = (
        "DROP TABLE IF EXISTS `notes`;"
    )


# ------------------------- It`s compulsory to keep order like: -------------------------
# TableParent, TableChild ...
# This order counts in `init_db.py` when tables create or drop.
tables: tuple = (TableUsers, TablePostRubrics, TablePosts, TableNoteRubrics, TableNotes,)
# ------------------------- ||||||||||||||||||||||||||||||||||| -------------------------


# ------------------------- INITIALIZE AND CLOSE MYSQL          -------------------------


async def init_mysql(app: aiohttp.web.Application) -> None:
    """ Create and set in app settings MySQL pool """
    db_config = app['config']['mysql']
    loop: asyncio.AbstractEventLoop = app['loop']

    port: int = int(db_config['port'])

    pool: aiomysql.Pool = await aiomysql.create_pool(
        host=db_config['host'],
        port=port,
        user=db_config['user_name'],
        password=db_config['user_password'],
        db=db_config['database'],
        loop=loop,
        autocommit=True
    )

    logger.success('Mysql pool is created.')

    app['db'] = pool

    logger.success('App database pool is established. The database ready to work!')


async def close_mysql(app: aiohttp.web.Application):
    """ Close database connection """
    app['db'].close()

    logger.info('App database pool is closing...')

    await app['db'].wait_closed()

    logger.success('App database pool is closed and all connections are finished!')


# ------------------------- ||||||||||||||||||||||||||||||||||| -------------------------
# ------------------------- SELECT QUERIES                      -------------------------


async def fetch_all_post_rubrics(
        connection: aiomysql.Connection, *args) -> List[Dict[str, Union[int, str]]]:
    """  Fetch all post rubrics for page """
    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            'SELECT * FROM `post_rubrics`;'
        )
        post_rubrics = await cursor.fetchall()
        return post_rubrics


async def fetch_posts_quantity(connection: aiomysql.Connection, *args) -> int:
    """  Fetch quantity of posts """
    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            'SELECT COUNT(*) FROM `posts`;'
        )
        query_result = await cursor.fetchone()
        posts_quantity = int(query_result[0])
        return posts_quantity


async def fetch_one_post(connection: aiomysql.Connection, post_id: int, *args
                         ) -> Dict[str, Union[int, str, datetime.datetime]]:
    """  Fetch the one particular post """
    async with connection.cursor() as cursor:
        await cursor.execute(
            'SELECT * FROM `posts` WHERE `id` = %()s;',
            {
                'id': post_id
            }
        )
        post = await cursor.fetchone()
        return post


async def fetch_one_random_post(connection: aiomysql.Connection, *args
                                ) -> Dict[str, Union[int, str, datetime.datetime]]:
    """  Fetch an one random post """
    order_key: float = random.random()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'SELECT * FROM `posts` ORDER BY %(order_key)s LIMIT 1;',
            {
                'order_key': order_key
            }
        )
        post = await cursor.fetchone()
        return post


async def fetch_all_posts(connection: aiomysql.Connection, *args
                          ) -> List[Dict[str, Union[int, str, datetime.datetime]]]:
    """ Fetch all posts """
    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            'SELECT * FROM `posts` ;'
        )
        posts = await cursor.fetchall()
        return posts


async def fetch_all_posts_for_page(connection: aiomysql.Connection, *args, page: int = 1, rows_quantity: int = 10
                                   ) -> List[Dict[str, Union[int, str, datetime.datetime]]]:
    """ Fetch all posts for page """
    offset = (page - 1) * rows_quantity

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            'SELECT * FROM `posts` LIMIT %(offset)s, %(row_count)s;',
            {
                'offset': offset,
                'row_count': rows_quantity
            }
        )
        posts_for_page = await cursor.fetchall()
        return posts_for_page


async def fetch_all_posts_by_rubric(connection: aiomysql.Connection, rubric_id: int, *args
                                    ) -> List[Dict[str, Union[int, str, datetime.datetime]]]:
    """ Fetch all posts by rubric """
    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            (
                'SELECT * FROM `posts` WHERE `post_rubric_id` = %(rubric_id)s '
                'ORDER BY `created_date` DESC;'
            ),
            {
                'rubric_id': rubric_id
            }
        )
        posts_by_rubric = await cursor.fetchall()
        return posts_by_rubric


async def fetch_all_posts_by_rubric_for_page(connection: aiomysql.Connection, rubric_id: int, *args, page: int = 1,
                                             rows_quantity: int = 10
                                             ) -> List[Dict[str, Union[int, str, datetime.datetime]]]:
    """ Fetch all posts by rubric for page """
    offset = (page - 1) * rows_quantity

    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            (
                'SELECT * FROM `posts` WHERE `post_rubric_id` = %(rubric_id)s '
                'ORDER BY `created_date` DESC LIMIT %(offset)s %(row_count)s;'
            ),
            {
                'rubric_id': rubric_id,
                'offset': offset,
                'row_count': rows_quantity
            }
        )
        posts_by_rubric_for_page = await cursor.fetchall()
        return posts_by_rubric_for_page


async def fetch_all_note_rubrics(connection: aiomysql.Connection, user_id: int
                                 ) -> List[Dict[str, Union[int, str]]]:
    """ Fetch all notes by rubric """
    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            'SELECT * FROM `note_rubrics` WHERE `user_id` = %(user_id)s ORDER BY `title`;',
            {
                'user_id': user_id
            }
        )
        note_rubrics = await cursor.fetchall()
        return note_rubrics


async def fetch_all_notes(connection: aiomysql.Connection, user_id: int
                          ) -> List[Dict[str, Union[int, str, datetime.datetime]]]:
    """ Fetch all notes """
    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            'SELECT * FROM `notes` WHERE `user_id` = %(user_id)s ORDER BY `created_date` DESC;',
            {
                'user_id': user_id
            }
        )
        notes = await cursor.fetchall()
        return notes


async def fetch_all_notes_by_rubric(connection: aiomysql.Connection, user_id: int, rubric_id: int
                                    ) -> List[Dict[str, Union[int, str, datetime.datetime]]]:
    """ Fetch all notes by rubric """
    async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
        await cursor.execute(
            (
                'SELECT * FROM `notes` WHERE `user_id` = %(user_id)s AND `note_rubric_id` = %(rubric_id)s '
                'ORDER BY `created_date` DESC;'
            ),
            {
                'user_id': user_id,
                'rubric_id': rubric_id
            }
        )
        notes_by_rubric = await cursor.fetchall()
        return notes_by_rubric


# ------------------------- ||||||||||||||||||||||||||||||||||| -------------------------
# ------------------------- INSERT QUERIES                      -------------------------
# async def insert_post_rubric(connection: aiomysql.Connection, user_id: int, *args) -> None:
#     """ Insert new post rubric """
#     pass
#
#
# async def insert_post(connection: aiomysql.Connection, user_id, title: str, content: str, rubric_id: int, *args
#                       ) -> None:
#     """ Insert new post """
#     pass
#
#
# async def insert_note_rubric(connection: aiomysql.Connection, user_id: int, title: str, *args) -> None:
#     """ Insert new note rubric """
#     pass
#
#
# async def insert_note(connection: aiomysql.Connection, user_id: int, title: str, content: str, rubric_id: int = None,
#                       *args
#                       ) -> None:
#     """ Insert new note """
#     pass
# ------------------------- ||||||||||||||||||||||||||||||||||| -------------------------
# ------------------------- UPDATE QUERIES                      -------------------------
# async def update_post_rubric(connection: aiomysql.Connection, post_rubric_id: int, title: str,  *args) -> None:
#     """ Update the post rubric """
#     pass
#
#
# async def update_post(connection: aiomysql.Connection, post_id: int, title: str, content: str, rubric_id: int, *args
#                       ) -> None:
#     """ Update the post """
#     pass
#
#
# async def update_note_rubric(connection: aiomysql.Connection, note_rubric_id: int, title: str, *args) -> None:
#     """ Update the note rubric """
#     pass
#
#
# async def update_note(connection: aiomysql.Connection, note_id: int, title: str, content: str, rubric_id: int = None,
#                       *args
#                       ) -> None:
#     """ Update the note """
#     pass
# ------------------------- ||||||||||||||||||||||||||||||||||| -------------------------
# ------------------------- DELETE QUERIES                      -------------------------
# async def delete_post_rubric(connection: aiomysql.Connection, post_rubric_id: int, *args) -> None:
#     """ Delete the post rubric """
#     pass
#
#
# async def delete_post(connection: aiomysql.Connection, post_id: int, *args) -> None:
#     """ Delete the post """
#     pass
#
#
# async def delete_note_rubric(connection: aiomysql.Connection, note_rubric_id: int, *args) -> None:
#     """ Delete the note rubric """
#     pass
#
#
# async def delete_note(connection: aiomysql.Connection, note_id: int, *args) -> None:
#     """ Delete the note """
#     pass
# ------------------------- ||||||||||||||||||||||||||||||||||| -------------------------
