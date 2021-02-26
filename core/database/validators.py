"""
Contains validation models.

.. class:: UserCreation(pydantic.BaseModel)
    implements user entity
.. class:: PostRubricCreation(pydantic.BaseModel)
    implements post rubric entity
.. class:: PostCreation(pydantic.BaseModel)
    implements post entity
.. class:: NoteRubricCreation(pydantic.BaseModel)
    implements note rubric entity
.. class:: NoteCreation(pydantic.BaseModel)
    implements note entity
.. class:: PostUrlParams(pydantic.BaseModel)
    implements post url params entity
.. class:: NoteUrlParams(pydantic.BaseModel)
    implements note url params entity

.. function:: get_formatted_error_message(validation_error: pydantic.ValidationError) -> str
    return formatted message about validation error
"""

from typing import Optional

import pydantic

from ..settings import (
    DEFAULT_POSTS_ON_PAGE,
    DEFAULT_NOTES_ON_PAGE
)


# possibility to create model instance by field names - not aliases | flag installed
pydantic.BaseConfig.allow_population_by_field_name = True


class UserAuthorization(pydantic.BaseModel):
    login: str = pydantic.fields.Field(min_length=6)
    password: str = pydantic.fields.Field(min_length=6)


class UserCreation(pydantic.BaseModel):
    login: str = pydantic.fields.Field(min_length=6)
    password: str = pydantic.fields.Field(min_length=6)


class PostRubricCreation(pydantic.BaseModel):
    user_id: int
    title: str = pydantic.fields.Field(min_length=3)


class PostRubricEditing(pydantic.BaseModel):
    title: str = pydantic.fields.Field(min_length=3)


class PostCreation(pydantic.BaseModel):
    user_id: int
    rubric_id: int
    title: str = pydantic.fields.Field(min_length=10)
    content: str = pydantic.fields.Field(min_length=10)


class PostEditing(pydantic.BaseModel):
    rubric_id: int
    title: str = pydantic.fields.Field(min_length=10)
    content: str = pydantic.fields.Field(min_length=10)


class NoteRubricCreation(pydantic.BaseModel):
    user_id: Optional[int]
    title: str = pydantic.fields.Field(min_length=3)


class NoteRubricEditing(pydantic.BaseModel):
    title: str = pydantic.fields.Field(min_length=3)


class NoteCreation(pydantic.BaseModel):
    user_id: int
    rubric_id: int
    content: str = pydantic.fields.Field(min_length=3)


class NoteEditing(pydantic.BaseModel):
    rubric_id: int
    content: str = pydantic.fields.Field(min_length=3)


class PostUrlParams(pydantic.BaseModel):
    page: Optional[int] = pydantic.fields.Field(alias='page_number', default=1)
    quantity: Optional[int] = pydantic.fields.Field(alias='rows_quantity', default=DEFAULT_POSTS_ON_PAGE)
    rubric: Optional[int] = pydantic.fields.Field(alias='rubric_id')
    keyword: Optional[str] = pydantic.fields.Field(alias='search_word')


class NoteUrlParams(pydantic.BaseModel):
    page: Optional[int] = pydantic.fields.Field(alias='page_number', default=1)
    quantity: Optional[int] = pydantic.fields.Field(alias='rows_quantity', default=DEFAULT_NOTES_ON_PAGE)
    rubric: Optional[int] = pydantic.fields.Field(alias='rubric_id')


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
