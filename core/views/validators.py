"""
Contains validating classes.


Classes {errors}:
    class InvalidParamValueError(ValueError):
    = raised when param has the incorrect data type (value) to converting
    --------------------------------------------------------------------------------------------------------------------
    class InvalidFormError(TypeError):
    = raised when POST request does not all expected params
    --------------------------------------------------------------------------------------------------------------------
Classes:
    class Param:
    = implements param object. Instances are used for validators
    --------------------------------------------------------------------------------------------------------------------
    class ParamsHandler:
    = validate params that get from a user by prepared params patterns (ParamsForValidating)
    --------------------------------------------------------------------------------------------------------------------
    class UrlParams(enum.Enum):
    = contains URL params that may be used in GET requests
    --------------------------------------------------------------------------------------------------------------------
    class FormPostRubric(enum.Enum):
    = implement post rubric form
    --------------------------------------------------------------------------------------------------------------------
    class FormPost(enum.Enum):
    = implement post form. (Post is not http method! It is database entity!)
    --------------------------------------------------------------------------------------------------------------------
    class FormNoteRubric(enum.Enum):
    = implement note rubric form
    --------------------------------------------------------------------------------------------------------------------
    class FormNote(enum.Enum):
    = implement note form
    --------------------------------------------------------------------------------------------------------------------
    class FormUser(enum.Enum):
    = implement user form
    --------------------------------------------------------------------------------------------------------------------
"""

from collections.abc import (
    Mapping
)
import enum
from typing import (
    Any,
    Optional,
    Type
)


class InvalidParamValueError(ValueError):
    """ Raised when param has the incorrect data type (value) to converting """


class InvalidFormError(TypeError):
    """ Raised when POST request does not all expected params """


class Param:
    """ Implements param object. Instances are used for validators """
    def __init__(self, param_name: str, param_type: type, new_param_name: Optional[str] = None):
        # the search in got data (url arguments, post form) will be carried out by
        self.name = param_name

        # expected data type of param
        self.type_ = param_type

        # new_name = key of final params dict
        # it is very useful to indicate this because param might be transmitted in other function,
        # with other argument names (e.g. db functions)
        # so, indicate this, if param name does not correspond to argument name in another function.
        self.new_name = new_param_name


class ParamsHandler:
    """ Validate params that get from a user by prepared params patterns (ParamsForValidating) """
    def __init__(self, params: Mapping, params_for_checking: Type[enum.Enum], http_method: str = 'GET') -> None:
        """
        Get `params` (input data from user) and `params_for_checking` (params that expected from a user).
        See `Param` class for familiarization with expected params (`params_for_checking`).

        Keyword `http_method`
            type: str
            possible arguments:
                - 'GET'     - not strict availability of all parameters
                - 'POST'    - strict availability of all parameters
        default: 'GET'

        if argument is not str type                     - TypeError raised,
        if argument is not in possible arguments list   - ValueError raised.
        """

        self.params = params
        self.params_for_checking = (param.value for param in params_for_checking)
        self.http_method = http_method

    @property
    def strict_availability_of_all_parameters(self) -> bool:
        """
        Based on `http_method` param return
        True (if POST method - strict availability of all parameters) or
        False (if GET method - not strict availability of all parameters).

        Raise:
            ValueError  (incorrect value of `http_method` argument)
            TypeError   (incorrect type of `http_method` argument)
        """

        if self.http_method == 'GET':
            status = False
        elif self.http_method == 'POST':
            status = True
        else:
            if isinstance(self.http_method, str):
                message = 'Argument `http_method` may have only value that in possible arguments list. '
                message += 'Check the function doc string!'
                raise ValueError(message)
            else:
                message = f'Argument `http_method` might be only str type. Not {type(self.http_method)}'
                raise TypeError(message)

        return status

    @property
    def validated_params(self) -> dict[str, Any]:
        """ Return validated params """
        return self.handle_params()

    def handle_params(self) -> dict[str, Any]:
        """
        Select in user data params that expected. Validate it.
        Return dict with validated params
        (param will be saved with new name if `new_param_name` in `Param` class indicated).

        Raise:
            InvalidFormError - if:
                - not all expected parameters received;
                - not all expected parameters have correct data type.
        """

        # dict for result params
        params = {}

        for param in self.params_for_checking:
            param_name, param_type, param_new_name = param.name, param.type_, param.new_name
            param_value = self.params.get(param_name)
            if param_value is None:
                if self.strict_availability_of_all_parameters:
                    message = 'Not all expected parameters received. Form is invalid!'
                    raise InvalidFormError(message)
            else:
                try:
                    converted_param_value = self.convert_param_type(param_value, param_type)
                except InvalidParamValueError:
                    if self.strict_availability_of_all_parameters:
                        message = 'Not all expected parameters have correct data type. Form is invalid!'
                        raise InvalidFormError(message)
                    else:
                        # incorrect value in url argument, might be logged
                        pass
                else:
                    if param_new_name:
                        param_name = param_new_name
                    params[param_name] = converted_param_value
        return params

    @staticmethod
    def convert_param_type(param: str, type_: type) -> Any:
        """
        Convert param in specified type.
        Raise `InvalidParameterTypeError` if param value does not correspond to given data type.
        """

        try:
            converted_argument = type_(param)
        except ValueError:
            raise InvalidParamValueError

        return converted_argument


class UrlParams(enum.Enum):
    """ Url params that may be used """
    rubric_id = Param('rubric', int, 'rubric_id')
    page_number = Param('page', int, 'page_number')
    rows_quantity = Param('quantity', int, 'rows_quantity')
    search_word = Param('keyword', str, 'search_word')


class FormPostRubric(enum.Enum):
    """ Post rubric form """
    user_id = Param('user_id', int)
    title = Param('title', str)


class FormPost(enum.Enum):
    """ Post form. (Post - entity! Not http method) """
    user_id = Param('user_id', int)
    title = Param('title', str)
    content = Param('content', str)
    rubric_id = Param('rubric_id', str)


class FormNoteRubric(enum.Enum):
    """ Note rubric form """
    user_id = Param('user_id', int)
    title = Param('title', str)


class FormNote(enum.Enum):
    """ Note form """
    user_id = Param('user_id', int)
    title = Param('title', str)
    content = Param('content', str)
    rubric_id = Param('rubric_id', int)


class FormUser(enum.Enum):
    """ Note rubric form """
    login = Param('login', str)
    password = Param('password', str)
