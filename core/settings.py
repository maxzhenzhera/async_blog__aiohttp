"""
Contains settings data (paths, config).

.. data:: CORE_DIR
.. data:: BASE_DIR
.. data:: STATIC_DIR
.. data:: IMAGES_DIR
.. data:: USER_IMAGES_DIR

.. data:: SERVER_HOST
.. data:: SERVER_PORT

.. data:: DB_NAME
.. data:: DB_USER
.. data:: DB_PASSWORD
.. data:: DB_HOST
.. data:: DB_PORT

.. data:: WEBSITE_ADMIN_LOGIN
.. data:: WEBSITE_ADMIN_PASSWORD

.. data:: DEFAULT_POSTS_ON_PAGE
.. data:: DEFAULT_NOTES_ON_PAGE
.. data:: DEFAULT_PAGE_NUMBERS_SEPARATOR
"""

import os
import pathlib

from dotenv import load_dotenv


load_dotenv()


CORE_DIR = pathlib.Path(__file__).parent
BASE_DIR = CORE_DIR.parent
STATIC_DIR = CORE_DIR / 'static'
IMAGES_DIR = STATIC_DIR / 'images'
USER_IMAGES_DIR = IMAGES_DIR / 'user_images'


SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = int(os.getenv('SERVER_PORT'))

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))


WEBSITE_ADMIN_LOGIN = os.getenv('WEBSITE_ADMIN_LOGIN')
WEBSITE_ADMIN_PASSWORD = os.getenv('WEBSITE_ADMIN_PASSWORD')


# default values for entire project
DEFAULT_POSTS_ON_PAGE = 10
DEFAULT_NOTES_ON_PAGE = 25

DEFAULT_PAGE_NUMBERS_SEPARATOR = '...'
# - - -
