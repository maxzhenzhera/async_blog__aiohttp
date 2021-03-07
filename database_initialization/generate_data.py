"""
Contains functions that generate needed data (like account for admin).

.. function:: create_admin_account(connection: aiomysql.Connection) -> None
    Create account for admin user.
"""

import aiomysql
from loguru import logger

from core import settings
from core.database import validators
from core.views import auth

CONFIG = settings.get_config()
WEBSITE_CONFIG = CONFIG['website']

ADMIN_LOGIN = WEBSITE_CONFIG['admin_login']
ADMIN_PASSWORD = WEBSITE_CONFIG['admin_password']


async def create_admin_account(connection: aiomysql.Connection) -> None:
    """
    Create website account for admin.

    :param connection: db connection
    :type connection: aiomysql.Connection

    :return: None
    :rtype: None
    """

    user_data = {
        'login': ADMIN_LOGIN,
        'password': ADMIN_PASSWORD
    }
    user = validators.UserCreation(**user_data)

    await auth.authorization.register_user(connection, user, user_is_admin=True)

    logger.success('Admin account is generated.')
