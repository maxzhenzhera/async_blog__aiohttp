"""
Contains implementing of pagination.

.. class:: Pagination:
    Implements pagination data (has useful property - Pagination().pagination_data - return all needed data)

.. const:: DEFAULT_PAGE_NUMBERS_SEPARATOR
    Value that will be displayed on the page between page numbers
"""

from typing import Union


from ..settings import DEFAULT_PAGE_NUMBERS_SEPARATOR


class Pagination:
    """ Implements pagination data """

    def __init__(self, possible_pages_quantity: int, page_number: int = 1) -> None:
        self.page_number = page_number
        self.possible_pages_quantity = possible_pages_quantity

    @property
    def pagination_data(self) -> dict[str, Union[int, None]]:
        """
        Return all pagination data needed for a template.

        :return: pagination data
        :rtype: dict[str, Union[int, None]]
        """

        pagination_data = {
            'first_page': 1 if self.page_number > 2 else None,
            'separator_after_first_page': DEFAULT_PAGE_NUMBERS_SEPARATOR if self.page_number > 3 else None,
            'previous_page_number': self.page_number - 1 if self.page_number > 1 else None,
            'page_number': self.page_number,
            'next_page_number': self.page_number + 1 if self.page_number < self.possible_pages_quantity else None,
            'separator_before_last_page':
                DEFAULT_PAGE_NUMBERS_SEPARATOR if self.possible_pages_quantity - self.page_number > 2 else None,
            'last_page': self.possible_pages_quantity if self.possible_pages_quantity - self.page_number > 1 else None
        }

        return pagination_data
