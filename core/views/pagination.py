"""
Contains implementing of pagination.


Classes:
    class Pagination:
    = implements pagination data (has useful property - Pagination().pagination - return all needed data)
    --------------------------------------------------------------------------------------------------------------------
Vars:
    DEFAULT_PAGE_NUMBERS_SEPARATOR: str | will be displayed on the page between page numbers
"""

import math
from typing import (
    Union
)

import aiomysql

from core.database import db


DEFAULT_PAGE_NUMBERS_SEPARATOR = '...'


class Pagination:
    """ Implements pagination data """
    def __init__(self, connection: aiomysql.Connection, entity: str, page_number: int = 1, rows_quantity: int = 10,
                 *args, **kwargs
                 ) -> None:
        """
        connection - db connection (to get rows quantity of entity)
        entity - name of entity (table in db, {posts, notes})
        page_number - number of active page
        rows_quantity - quantity of rows on page
        """
        self.connection = connection
        self.entity = entity
        self.page_number = page_number
        self.rows_quantity_for_page = rows_quantity

    async def count_pages_quantity(self) -> int:
        """ Count possible pages quantity """
        entity_rows_quantity = await db.fetch_rows_quantity(connection=self.connection, entity=self.entity)
        possible_pages_quantity = math.ceil(entity_rows_quantity / self.rows_quantity_for_page)
        return possible_pages_quantity

    @property
    async def pagination(self) -> dict[str, Union[int, None]]:
        """ Return all pagination data needed for a template """
        possible_pages_quantity = await self.count_pages_quantity()

        pagination_data = {
            'first_page': 1 if self.page_number > 2 else None,
            'separator_after_first_page': DEFAULT_PAGE_NUMBERS_SEPARATOR if self.page_number > 3 else None,
            'previous_page_number': self.page_number - 1 if self.page_number > 1 else None,
            'page_number': self.page_number,
            'next_page_number': self.page_number + 1 if self.page_number < possible_pages_quantity else None,
            'separator_before_last_page':
                DEFAULT_PAGE_NUMBERS_SEPARATOR if possible_pages_quantity - self.page_number > 2 else None,
            'last_page': possible_pages_quantity if possible_pages_quantity - self.page_number > 1 else None
        }
        return pagination_data
