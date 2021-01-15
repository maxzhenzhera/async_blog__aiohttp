from aiohttp import web
import aiohttp_jinja2
import jinja2

from core.middlewares import setup_middlewares
from core.routes import setup_routes
from core.settings import get_config


async def init_app():
    """ Prepare app to run """
    app = web.Application()

    app['config'] = get_config()

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('core', 'templates')
    )

    # create db connection on startup, shutdown on exit
    # app.on_startup.append(init_pg)
    # app.on_cleanup.append(close_pg)

    # setup views and routes
    setup_routes(app)

    setup_middlewares(app)

    return app


def main():
    """ Initialize and run app """
    # logger settings set

    app = init_app()

    config = get_config()
    web.run_app(
        app,
        host=config["server"]['host'],
        port=config["server"]['port']
    )


if __name__ == '__main__':
    main()
