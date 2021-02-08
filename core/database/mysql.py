"""
Contains functions that manage MySql connection (actions on start and on shut).


Functions:
    async def init_mysql(app: aiohttp.web.Application) -> None:
    --------------------------------------------------------------------------------------------------------------------
    async def close_mysql(app: aiohttp.web.Application):
    --------------------------------------------------------------------------------------------------------------------
"""

import asyncio
import aiomysql
import aiohttp.web
from loguru import logger


async def init_mysql(app: aiohttp.web.Application) -> None:
    """ Create and set in app settings MySQL pool """
    db_config = app['config']['mysql']
    loop: asyncio.AbstractEventLoop = app['loop']

    pool: aiomysql.Pool = await aiomysql.create_pool(
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