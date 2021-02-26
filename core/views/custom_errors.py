"""
Contains custom error handlers.

.. function:: handle_401(request) -> aiohttp.web.Response
    Handle 401 http error
.. function:: handle_403(request) -> aiohttp.web.Response
    Handle 403 http error
.. function:: handle_404(request) -> aiohttp.web.Response
    Handle 404 http error
.. function:: handle_405(request) -> aiohttp.web.Response
    Handle 405 http error
.. function:: handle_500(request) -> aiohttp.web.Response
    Handle 500 http error

.. const:: errors
    Mapping of pairs [http_code, error_handler]
"""

import aiohttp.web
import aiohttp_jinja2


__all__ = ['errors', ]


async def handle_401(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """ Handle http error {401 Unauthorized} and return response with prepared template """
    data = {
        'first_digit': 4,
        'second_digit': 0,
        'third_digit': 1,
        'message': 'Please, login first!'
    }

    return aiohttp_jinja2.render_template('error.html', request, data, status=401)


async def handle_403(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """ Handle http error {403 Forbidden} and return response with prepared template """
    data = {
        'first_digit': 4,
        'second_digit': 0,
        'third_digit': 3,
        'message': 'Sorry, but it is forbidden for you :)'
    }

    return aiohttp_jinja2.render_template('error.html', request, data, status=403)


async def handle_404(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """ Handle http error {404 Not Found} and return response with prepared template """
    data = {
        'first_digit': 4,
        'second_digit': 0,
        'third_digit': 4,
        'message': 'Hmm... We are lost!'
    }

    return aiohttp_jinja2.render_template('error.html', request, data, status=404)


async def handle_405(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """ Handle http error {405 Method Not Allowed} and return response with prepared template """
    data = {
        'first_digit': 4,
        'second_digit': 0,
        'third_digit': 5,
        'message': 'You on a wrong way! This method not allowed!'
    }

    return aiohttp_jinja2.render_template('error.html', request, data, status=405)


async def handle_500(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """ Handle http error {500 Internal Server Error} and return response with prepared template """
    data = {
        'first_digit': 5,
        'second_digit': 0,
        'third_digit': 0,
        'message': 'It is not you. It is me :) Sorry!'
    }

    return aiohttp_jinja2.render_template('error.html', request, data, status=500)


errors = {
    401: handle_401,
    403: handle_403,
    404: handle_404,
    405: handle_405,
    500: handle_500
}
