"""
Contains common views errors.

.. exception:: InvalidFormData(Exception)
    Raised when form data is invalid
"""


class InvalidFormDataError(Exception):
    """
    Raised when form data is invalid.

    Examples:
        - it is not needed param in form data;
        - it is expected to get only validated data (for almost all forms work redirects with exactly validation error
            that shows on the form page hints to fix, so, it is might be some exceptions)

    Do not confuse this error with the error that raised during data validation (pydantic.ValidationError like).

    So, it is might be used instead of the explicit `aiohttp.web.HTTPBadRequest` for more local context understanding.

    But, finally, in middlewares it will re-raise exactly `aiohttp.web.HTTPBadRequest` (already in the global context).
    """
