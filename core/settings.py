"""
Contain project path, config path and function that return config in `dict` format.


Functions:
    def get_config | () -> configparser.ConfigParser | Parse .ini file with settings in ConfigParser object that
    imitate `dict` work
    --------------------------------------------------------------------------------------------------------------------
Vars:
    BASE_DIR: pathlib.Path | contains path to project directory
    --------------------------------------------------------------------------------------------------------------------
    DEFAULT_CONFIG_PATH: pathlib.Path | contains path to config
    --------------------------------------------------------------------------------------------------------------------
    DEFAULT_POSTS_ON_PAGE: int, DEFAULT_NOTES_ON_PAGE: int | simple constants
    --------------------------------------------------------------------------------------------------------------------
"""


import configparser
import pathlib


BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'config.ini'

# default values for entire project
DEFAULT_POSTS_ON_PAGE = 10
DEFAULT_NOTES_ON_PAGE = 20


def get_config() -> configparser.ConfigParser:
    """ Get config from config file """
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)
    return config
