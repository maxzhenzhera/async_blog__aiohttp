import configparser
import pathlib


BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'config.ini'


def get_config():
    """ Get config from config file """
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)
    return config
