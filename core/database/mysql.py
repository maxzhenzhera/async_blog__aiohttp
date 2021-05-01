"""
Contains functions that manage MySql connection (actions on start and on shut).

.. function:: init_mysql(app: aiohttp.web.Application) -> None
    Create and set in app settings MySQL pool
.. function:: close_mysql(app: aiohttp.web.Application) -> None
    Close database connection
"""

import logging

import aiohttp.web
import aiomysql

from ..settings import (
    DB_NAME,
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD
)


logger = logging.getLogger(__name__)


async def init_mysql(app: aiohttp.web.Application) -> None:
    """
    Create and set in app settings MySQL pool.

    :param app: instance of the web application
    :type app: aiohttp.web.Application

    :return: None
    :rtype: None
    """

    pool: aiomysql.Pool = await aiomysql.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        autocommit=True
    )

    app['db'] = pool

    logger.info('Db pool has been set!')


async def close_mysql(app: aiohttp.web.Application) -> None:
    """
    Close database connection.

    :param app:
    :type app:

    :return: None
    :rtype: None
    """

    app['db'].close()
    await app['db'].wait_closed()
