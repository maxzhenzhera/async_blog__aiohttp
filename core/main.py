"""
Initializes app.

.. function:: init_app() -> aiohttp.web.Application
    setup settings for app
.. function:: main() -> None
    run app
"""

import aiohttp
import aiohttp.web
import aiohttp_jinja2
import jinja2
from loguru import logger

from .database.mysql import init_mysql, close_mysql
from .middlewares import setup_middlewares
from .routes import setup_routes
from .settings import (
    get_config,
    ERROR_LOG
)


async def init_app() -> aiohttp.web.Application:
    """
    Prepare app to run (setup all settings and create db connection).

    :return: configured instance of the web application
    :rtype: aiohttp.web.Application
    """

    app = aiohttp.web.Application()

    # set app config
    app['config'] = get_config()

    # set logger
    logger.add(ERROR_LOG, level='ERROR')
    app['logger'] = logger

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('core')
    )

    # create db connection on startup, shutdown on exit
    app.on_startup.append(init_mysql)
    app.on_cleanup.append(close_mysql)

    # setup views and routes
    setup_routes(app)

    # setup middlewares
    setup_middlewares(app)

    return app


def main() -> None:
    """
    Run app.

    :return: None
    :rtype: None
    """

    app = init_app()

    config = get_config()
    aiohttp.web.run_app(
        app,
        host=config["server"]['host'],
        port=int(config["server"]['port'])
    )
