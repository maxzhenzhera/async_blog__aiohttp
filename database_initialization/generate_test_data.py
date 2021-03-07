"""
Contains functions that help in development by quick generating test data.

.. function:: generate_users(connection: aiomysql.Connection) -> None
    Generate users
.. function:: generate_post_rubrics(connection: aiomysql.Connection) -> None
    Generate post rubrics
.. function:: generate_posts(connection: aiomysql.Connection) -> None
    Generate posts
.. function:: generate_test_data(connection: aiomysql.Connection) -> None
    Generate all wrote above
"""

import aiomysql
from loguru import logger

from . import test_data


async def generate_users(connection: aiomysql.Connection) -> None:
    async with connection.cursor() as cursor:
        await cursor.execute(test_data.query_to_create_users)


async def generate_post_rubrics(connection: aiomysql.Connection) -> None:
    async with connection.cursor() as cursor:
        await cursor.execute(test_data.query_to_create_post_rubrics)


async def generate_posts(connection: aiomysql.Connection) -> None:
    async with connection.cursor() as cursor:
        await cursor.execute(test_data.query_to_create_posts)


async def generate_test_data(connection: aiomysql.Connection) -> None:
    await generate_users(connection)
    await generate_post_rubrics(connection)
    await generate_posts(connection)

    logger.success('Test data is generated.')
