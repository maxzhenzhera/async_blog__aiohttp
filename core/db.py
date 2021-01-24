"""
Keeps classes that implement the database objects. `Database` and `TableName` contain only sql queries.

# # For future = sql queries will be used in some `Executor` class
# # that get connection in __init__ and then use it in methods

Classes:
    class Database | Contains queries that create/drop database, database`s user
    --------------------------------------------------------------------------------------------------------------------
    class TableUsers        | classes like  `TableName` implement one entity:
    ------------------------- each class contains queries that create/drop table (for now).
    class TablePostRubrics  |
    -------------------------
    class TablePosts        |
    -------------------------
    class TableNoteRubrics  |
    -------------------------
    class TableNotes        |
    --------------------------------------------------------------------------------------------------------------------
Functions:
    async def init_mysql | (app: aiohttp.web.Application, loop: asyncio.AbstractEventLoop) -> None |
    init mysql connection (create pool)
    --------------------------------------------------------------------------------------------------------------------
    async def close_mysql | (app: aiohttp.web.Application) | close mysql connection (close pool)
    --------------------------------------------------------------------------------------------------------------------
Vars:
    tables: tuple | contains all database tables in order (ParentTable, ChildTable)
    --------------------------------------------------------------------------------------------------------------------
"""

import asyncio

import aiohttp.web
import aiomysql
from loguru import logger


__all__ = ['Database', 'tables']
# `tables` in the end of classes


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
        "DROP USER IF EXISTS {user_name};                                       "
        "CREATE USER IF NOT EXISTS {user_name} IDENTIFIED BY '{user_password}'; "
        "GRANT ALL PRIVILEGES ON {db_name}.* TO {user_name} WITH GRANT OPTION;  "
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
        "    `id` INT NOT NULL,                                                                     "
        "    `content` VARCHAR(255) NOT NULL,                                                       "
        "    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,                            "
        "    `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, "
        "    `note_rubric_id` INT NULL,                                                             "
        "    `users_id` INT NOT NULL,                                                               "
        "    PRIMARY KEY (`id`),                                                                    "
        "    FOREIGN KEY (`note_rubric_id`)                                                         "
        "        REFERENCES `note_rubrics` (`id`)                                                   "
        "        ON DELETE CASCADE ON UPDATE NO ACTION,                                             "
        "    FOREIGN KEY (`users_id`)                                                               "
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


async def init_mysql(app: aiohttp.web.Application, loop: asyncio.AbstractEventLoop) -> None:
    """ Create and set in app settings MySQL pool """
    db_config = app['config']['mysql']
    pool = await aiomysql.create_pool(
        host=db_config['host'],
        port=int(db_config['port']),
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
