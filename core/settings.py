"""
Contains settings data (paths, config).

.. function:: get_config() -> configparser.ConfigParser
    Parse .ini file with settings in ConfigParser object that imitate `dict` work

.. const:: BASE_DIR: pathlib.Path
    Contains path to project directory
.. const:: DEFAULT_CONFIG_PATH: pathlib.Path
    Contains path to config
.. const:: DEFAULT_POSTS_ON_PAGE
    Default value of the posts quantity on page
.. const:: DEFAULT_NOTES_ON_PAGE
    Default value of the notes quantity on page
"""

import configparser
import pathlib


BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'config.ini'

# default values for entire project
DEFAULT_POSTS_ON_PAGE = 10
DEFAULT_NOTES_ON_PAGE = 20


def get_config() -> configparser.ConfigParser:
    """
    Get config from config file.

    :return: config object with interface like dict
    :rtype: configparser.ConfigParser
    """

    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)

    return config
