"""
Setups, drops database (database, user, tables).

.. async:: create_tables(connection: aiomysql.Connection) -> None
.. async:: drop_tables(connection: aiomysql.Connection) -> None
.. func:: dump_sql_of_tables_creation()
.. async:: main() -> None
"""

import pathlib
import sys


# add package to global path -------------------------------------------------------------------------------------------
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
# ----------------------------------------------------------------------------------------------------------------------


import asyncio
import datetime
import logging

import aiomysql

from core.database import models
from core.security import hash_password
from core.settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    WEBSITE_ADMIN_LOGIN,
    WEBSITE_ADMIN_PASSWORD
)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


SQL_DUMP_DIR = pathlib.Path(__file__).parent / 'sql'
SQL_DUMP_DIR.mkdir(parents=True, exist_ok=True)
SQL_TABLES_DUMP_FILEPATH = SQL_DUMP_DIR / '!init_tables.sql'
SQL_ADMIN_ACCOUNT_DUMP_FILEPATH = SQL_DUMP_DIR / 'init_admin_account.sql'


async def create_tables(connection: aiomysql.Connection) -> None:
    """ Create all tables in the database """
    stmt = '\n'.join([table.create_table for table in models.tables])

    async with connection.cursor() as cursor:
        await cursor.execute(stmt)

    logger.info('Tables have been created!')


async def drop_tables(connection: aiomysql.Connection) -> None:
    """ Drop all tables in the database """
    stmt = '\n'.join(reversed([table.drop_table for table in models.tables]))

    async with connection.cursor() as cursor:
        await cursor.execute(stmt)

    logger.info('Tables have been dropped!')


async def create_website_admin(connection: aiomysql.Connection) -> None:
    """ Create admin account """
    stmt = " INSERT INTO `users` (`login`, `password`, `is_admin`) VALUES (%(login)s, %(password)s, %(is_admin)s) "
    params = {
        'login': WEBSITE_ADMIN_LOGIN,
        'password': hash_password(WEBSITE_ADMIN_PASSWORD),
        'is_admin': True
    }
    cursor: aiomysql.Cursor
    async with connection.cursor() as cursor:
        await cursor.execute(stmt, params)

    logger.info('Admin account have been created!')


def dump_sql_of_tables_creation() -> None:
    """ Dump sql code of tables creation """
    sql_dump = '\n'.join([table.create_table for table in models.tables])
    dump_comment = (
        '/*'
        f'\n\tModels version: {models.__version__}'
        f'\n\tGeneration time: {datetime.datetime.now().isoformat()}'
        '\n*/\n'
    )

    with open(SQL_TABLES_DUMP_FILEPATH, 'w') as file:
        file.write(dump_comment)
        file.write(sql_dump)

    logger.info(f'Sql dump of tables creation is ready! To see - check: {SQL_TABLES_DUMP_FILEPATH}')


async def dump_sql_of_admin_account_creation(connection: aiomysql.Connection) -> None:
    """ Dump sql code of tables creation """
    stmt = " INSERT INTO `users` (`login`, `password`, `is_admin`) VALUES (%(login)s, %(password)s, %(is_admin)s); "
    params = {
        'login': WEBSITE_ADMIN_LOGIN,
        'password': hash_password(WEBSITE_ADMIN_PASSWORD),
        'is_admin': True
    }

    async with connection.cursor() as cursor:
        query = stmt % cursor._escape_args(params, connection)

    sql_dump = query
    dump_comment = (
        '/*'
        f'\n\tGeneration time: {datetime.datetime.now().isoformat()}'
        '\n*/\n'
    )

    with open(SQL_ADMIN_ACCOUNT_DUMP_FILEPATH, 'w') as file:
        file.write(dump_comment)
        file.write(sql_dump)

    logger.info(f'Sql dump of website admin account is ready! To see - check: {SQL_ADMIN_ACCOUNT_DUMP_FILEPATH}')


async def main() -> None:
    """ Invoke functions that operate with database """
    connection = await aiomysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        autocommit=True
    )

    await drop_tables(connection)
    await create_tables(connection)
    await create_website_admin(connection)

    await dump_sql_of_admin_account_creation(connection)
    dump_sql_of_tables_creation()

    connection.close()


if __name__ == '__main__':
    asyncio.run(main())
