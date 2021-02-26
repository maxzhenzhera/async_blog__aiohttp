"""
Contains functions that manage MySql connection (actions on start and on shut).

.. function:: init_mysql(app: aiohttp.web.Application) -> None
    Create and set in app settings MySQL pool
.. function:: close_mysql(app: aiohttp.web.Application) -> None
    Close database connection
"""

import aiohttp.web
import aiomysql


async def init_mysql(app: aiohttp.web.Application) -> None:
    """
    Create and set in app settings MySQL pool.

    :param app: instance of the web application
    :type app: aiohttp.web.Application

    :return: None
    :rtype: None
    """

    db_config = app['config']['mysql']

    pool: aiomysql.Pool = await aiomysql.create_pool(
        host=db_config['host'],
        port=int(db_config['port']),
        user=db_config['user_name'],
        password=db_config['user_password'],
        db=db_config['database'],
        autocommit=True
    )

    app['db'] = pool


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
