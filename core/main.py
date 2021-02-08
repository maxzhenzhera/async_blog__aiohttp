"""
Heart of project. Run the point of the app is here (also '__main__' available).


Functions:
    async def init_app() -> aiohttp.web.Application:
    = setup settings for app
    --------------------------------------------------------------------------------------------------------------------
    def main() -> None:
    = run app
    --------------------------------------------------------------------------------------------------------------------
"""

import asyncio

import aiohttp
import aiohttp.web
import aiohttp_jinja2
import jinja2
from loguru import logger

from core.database.mysql import init_mysql, close_mysql
from core.middlewares import setup_middlewares
from core.routes import setup_routes
from core.settings import get_config


async def init_app() -> aiohttp.web.Application:
    """ Prepare app to run (setup all settings and create db connection) """
    app = aiohttp.web.Application()
    loop: asyncio.AbstractEventLoop = app.get('loop')

    # set app config
    app['config'] = get_config()
    app['loop'] = loop
    logger.success('Config is gotten.')

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('core', 'templates')
    )
    logger.success('Template renderer is established.')

    # create db connection on startup, shutdown on exit
    logger.info('Database connection is doing...')
    app.on_startup.append(init_mysql)
    app.on_cleanup.append(close_mysql)
    logger.success('Database connection is established. Creation and clean up processes is scheduled.')

    # setup views and routes
    setup_routes(app)
    logger.success('Views and routes are established.')

    # setup middlewares
    setup_middlewares(app)
    logger.success('Middlewares are established.')

    return app


def main() -> None:
    """ Initialize and run app """
    # logger settings set might be here

    app = init_app()

    config = get_config()
    aiohttp.web.run_app(
        app,
        host=config["server"]['host'],
        port=int(config["server"]['port'])
    )
    logger.success('APP IS RUNNING!')


if __name__ == '__main__':
    main()
