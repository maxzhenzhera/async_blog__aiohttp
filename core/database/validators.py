"""
Contains validation models.

.. class:: UserAuthorization(pydantic.BaseModel)
    Implement validation model
.. class:: UserCreation(pydantic.BaseModel)
    Implement validation model
.. class:: UserSettingsEditingLogin(pydantic.BaseModel)
    Implement validation model
.. class:: UserSettingsEditingInfo(pydantic.BaseModel)
    Implement validation model
.. class:: UserSettingsEditingPassword(pydantic.BaseModel)
    Implement validation model
.. class:: FileIsImage(pydantic.BaseModel)
    Implement validation model
.. class:: PostRubricCreation(pydantic.BaseModel)
    Implement validation model
.. class:: PostRubricEditing(pydantic.BaseModel)
    Implement validation model
.. class:: PostCreation(pydantic.BaseModel)
    Implement validation model
.. class:: PostEditing(pydantic.BaseModel)
    Implement validation model
.. class:: NoteRubricCreation(pydantic.BaseModel)
    Implement validation model
.. class:: NoteRubricEditing(pydantic.BaseModel)
    Implement validation model
.. class:: NoteCreation(pydantic.BaseModel)
    Implement validation model
.. class:: NoteEditing(pydantic.BaseModel)
    Implement validation model
.. class:: PostUrlParams(pydantic.BaseModel)
    Implement validation model
.. class:: NoteUrlParams(pydantic.BaseModel)
    Implement validation model

.. function:: convert_empty_value(param: Any) -> Union[Any, None]
    Convert values (express that value is empty) in None
.. function:: get_formatted_error_message(validation_error: pydantic.ValidationError) -> str
    return formatted message about validation error

.. const:: IMAGE_EXTENSIONS
    Contains set of the image ext-s
"""

import os.path
from typing import (
    Any,
    Union,
    Optional
)

import pydantic

from ..settings import (
    DEFAULT_POSTS_ON_PAGE,
    DEFAULT_NOTES_ON_PAGE
)


# possibility to create model instance by field names - not aliases | flag installed
pydantic.BaseConfig.allow_population_by_field_name = True


# constants
IMAGE_EXTENSIONS = {'.png', '.jpeg', '.jpg'}


# common validators


def convert_empty_value(param: Any) -> Union[Any, None]:
    """
    Convert empty value to None.

    :param param: param
    :type param: Any

    :return: native value if value is not empty else None
    :rtype: Union[Any, None]
    """

    #  params is None or False | param has int value: -1 | param has string value: 'None'
    if not param or param == -1 or param == 'None':
        return None

    return param


# common fields


USER_LOGIN_TYPE = pydantic.fields.Field(min_length=5, max_length=255)
USER_PASSWORD_TYPE = pydantic.fields.Field(min_length=5, max_length=255)


# models


class UserAuthorization(pydantic.BaseModel):
    login: str = USER_LOGIN_TYPE
    password: str = USER_PASSWORD_TYPE


class UserCreation(pydantic.BaseModel):
    login: str = USER_LOGIN_TYPE
    password: str = USER_PASSWORD_TYPE


class UserSettingsEditingLogin(pydantic.BaseModel):
    new_login: str = USER_LOGIN_TYPE


class UserSettingsEditingInfo(pydantic.BaseModel):
    new_about_me: Optional[str]


class UserSettingsEditingPassword(pydantic.BaseModel):
    new_password: str = USER_PASSWORD_TYPE


class FileIsImage(pydantic.BaseModel):
    filename: str

    @pydantic.validator('filename')
    def is_file_with_image_extension(cls, filename):
        _, file_ext = os.path.splitext(filename)

        if file_ext in IMAGE_EXTENSIONS:
            return filename

        raise ValueError('unsupported extension of the image; supported: {}'.format(' | '.join(IMAGE_EXTENSIONS)))


class PostRubricCreation(pydantic.BaseModel):
    user_id: int
    title: str = pydantic.fields.Field(min_length=3, max_length=255)


class PostRubricEditing(pydantic.BaseModel):
    title: str = pydantic.fields.Field(min_length=3, max_length=255)


class PostCreation(pydantic.BaseModel):
    user_id: int
    rubric_id: Optional[int]
    title: str = pydantic.fields.Field(min_length=5, max_length=255)
    content: str = pydantic.fields.Field(min_length=5)

    # validators
    _convert_empty_values = pydantic.validator('rubric_id', allow_reuse=True, pre=True)(convert_empty_value)


class PostEditing(pydantic.BaseModel):
    rubric_id: Optional[int]
    title: str = pydantic.fields.Field(min_length=5, max_length=255)
    content: str = pydantic.fields.Field(min_length=5)

    # validators
    _convert_empty_values = pydantic.validator('rubric_id', allow_reuse=True, pre=True)(convert_empty_value)


class NoteRubricCreation(pydantic.BaseModel):
    user_id: Optional[int]
    title: str = pydantic.fields.Field(min_length=3, max_length=255)


class NoteRubricEditing(pydantic.BaseModel):
    title: str = pydantic.fields.Field(min_length=3, max_length=255)


class NoteCreation(pydantic.BaseModel):
    user_id: int
    rubric_id: Optional[int]
    content: str = pydantic.fields.Field(min_length=3)

    # validators
    _convert_empty_values = pydantic.validator('rubric_id', allow_reuse=True, pre=True)(convert_empty_value)


class NoteEditing(pydantic.BaseModel):
    rubric_id: Optional[int]
    content: str = pydantic.fields.Field(min_length=3)

    # validators
    _convert_empty_values = pydantic.validator('rubric_id', allow_reuse=True, pre=True)(convert_empty_value)


class PostUrlParams(pydantic.BaseModel):
    page: Optional[int] = pydantic.fields.Field(alias='page_number', default=1)
    quantity: Optional[int] = pydantic.fields.Field(alias='rows_quantity', default=DEFAULT_POSTS_ON_PAGE)
    rubric: Optional[int] = pydantic.fields.Field(alias='rubric_id')
    keyword: Optional[str] = pydantic.fields.Field(alias='search_word')
    thinker: Optional[int] = pydantic.fields.Field(alias='user_id')


class NoteUrlParams(pydantic.BaseModel):
    page: Optional[int] = pydantic.fields.Field(alias='page_number', default=1)
    quantity: Optional[int] = pydantic.fields.Field(alias='rows_quantity', default=DEFAULT_NOTES_ON_PAGE)
    rubric: Optional[int] = pydantic.fields.Field(alias='rubric_id')
    keyword: Optional[str] = pydantic.fields.Field(alias='search_word')


def get_formatted_error_message(validation_error: pydantic.ValidationError) -> str:
    """
    Return formatted message about validation errors.

    :param validation_error: error that was raised on validation
    :type validation_error: pydantic.ValidationError

    :return: formatted, user readable message
    :rtype: str
    """

    message = '\n'.join(
        [f"{error['loc'][0]:<10} - {error['msg']}" for error in validation_error.errors()]
    )

    return message
