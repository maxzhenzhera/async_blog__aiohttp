"""
Contains useful classes and functions separated from main modules.


Classes:
     class InvalidParameterTypeError | (Exception) |  Raises when URL parameter has the incorrect data type
    --------------------------------------------------------------------------------------------------------------------
    class UrlParam | Contains data about needed url param
    --------------------------------------------------------------------------------------------------------------------
    class UrlParamsHandler | Handles url params
    --------------------------------------------------------------------------------------------------------------------
"""


from collections.abc import MutableMapping
from typing import (
    Any,
    Iterable
)

import aiohttp.web
from loguru import logger


class InvalidParameterTypeError(Exception):
    """ Raises when URL parameter has the incorrect data type """


class UrlParam:
    """ Implements url param object. Instances are used for `UrlParamsHandler` """
    def __init__(self, param_name: str, param_type: type, new_param_name: str = ''):
        self.name = param_name
        self.type_ = param_type
        self.new_name = new_param_name


class UrlParamsHandler:
    """ Handles url query, parse, convert and validate params by input type """
    def __init__(self, request: aiohttp.web.Request, url_params_for_checking: Iterable[UrlParam]) -> None:
        self.request = request
        self.request_url_params: MutableMapping = request.rel_url.query
        self.url_params_for_checking = url_params_for_checking
        self.params = self.handle_url_params()

    def handle_url_params(self) -> dict[str, Any]:
        """
        Look over request params, among them search given params (needed), then convert and validate found params.
        All needed params return in `dict` (if in `UrlParam` object of `url_params_for_checking` set `new_name`, then
        param will be saved in result with new given name, else param name will have remained unchanged).
        """

        params = {}

        # url_param: UrlParam
        for url_param in self.url_params_for_checking:
            param_name, param_type, param_new_name = url_param.name, url_param.type_, url_param.new_name
            param_value = self.request_url_params.get(param_name)
            if param_value is None:
                # url argument is absent
                pass
            else:
                try:
                    converted_param_value = self.convert_param_type(param_value, param_type)
                except InvalidParameterTypeError:
                    message = 'In request {request} passed incorrect type of parameter(s) from {peer}'
                    logger.info(message.format(request=self.request.url, peer=self.request.remote))
                else:
                    if param_new_name:
                        params[param_new_name] = converted_param_value
                    else:
                        params[param_name] = converted_param_value
        return params

    @staticmethod
    def convert_param_type(param: str, type_: type) -> Any:
        """
        Convert url param in given data type.
        Raise `InvalidParameterTypeError` if param type does not correspond to given data type.
        """

        try:
            converted_argument = type_(param)
        except ValueError:
            raise InvalidParameterTypeError

        return converted_argument
