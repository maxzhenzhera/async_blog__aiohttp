"""
Initialize (create db, tables, new role) and implement deleting all this stuff.
As we don`t use ORM like SQLAlchemy, most of the needed SQL code is saved in a particular directory.
"""

import asyncio

import aiomysql
from loguru import logger

from core.db import Database, tables
from core.settings import BASE_DIR, get_config


USER_CONFIG_PATH = BASE_DIR / 'config' / 'config.ini'
USER_CONFIG = get_config()
DATABASE_CONFIG = USER_CONFIG['mysql']

DB_NAME: str = DATABASE_CONFIG['database']
DB_HOST: str = DATABASE_CONFIG['host']
DB_PORT: int = int(DATABASE_CONFIG['port'])
DB_USER_NAME: str = DATABASE_CONFIG['user_name']
DB_USER_PASSWORD: str = DATABASE_CONFIG['user_password']

# data for first set up (used `root` user for creating database and user)
DB_ROOT_NAME: str = DATABASE_CONFIG['root_name']
DB_ROOT_PASSWORD: str = DATABASE_CONFIG['root_password']


async def setup_db(connection: aiomysql.Connection) -> None:
    """ Creates database, tables and user """
    query_create_database = Database.create_database.format(
        db_name=DB_NAME
    )

    async with connection.cursor() as cursor:
        await cursor.execute(query_create_database)

    await create_tables(connection)
    await create_user(connection)


async def teardown_db(connection: aiomysql.Connection) -> None:
    """ Drops the entire base """
    query_drop_database = Database.drop_database.format(
        db_name=DB_NAME
    )

    async with connection.cursor() as cursor:
        await cursor.execute(query_drop_database)

    await drop_user(connection)


async def create_tables(connection: aiomysql.Connection) -> None:
    """ Creates all tables in the database """
    query_use_database = "USE {db_name}".format(db_name=DB_NAME)

    async with connection.cursor() as cursor:
        await cursor.execute(query_use_database)
        for table in tables:
            await cursor.execute(table.create_table)


async def drop_tables(connection: aiomysql.Connection) -> None:
    """ Drops all tables in the database """
    query_use_database = "USE {db_name}".format(db_name=DB_NAME)

    async with connection.cursor() as cursor:
        await cursor.execute(query_use_database)
        for table in tables:
            await cursor.execute(table.drop_table)


async def create_user(connection: aiomysql.Connection) -> None:
    """ Creates user that lead the app database """
    query_create_user = Database.create_user.format(
        db_name=DB_NAME,
        user_name=DB_USER_NAME,
        user_password=DB_USER_PASSWORD
    )

    async with connection.cursor() as cursor:
        await cursor.execute(query_create_user)


async def drop_user(connection: aiomysql.Connection) -> None:
    """ Drops user that lead the app database """
    query_drop_user = Database.drop_user.format(
        user_name=DB_USER_NAME,
    )

    async with connection.cursor() as cursor:
        await cursor.execute(query_drop_user)


async def main(loop: asyncio.AbstractEventLoop) -> None:
    """ All functions described above can be used here """
    connection = await aiomysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_ROOT_NAME,
        password=DB_ROOT_PASSWORD,
        loop=loop,
        autocommit=True
    )

    await teardown_db(connection)

    # await setup_db(connection)

    # --------------------------------------------------
    # # await drop_tables(cursor)
    # # await teardown_db(cursor)
    # --------------------------------------------------

    connection.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
