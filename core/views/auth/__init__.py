"""
Contains modules that control registering, authorizing and authentication processes.
"""

# modules will be available to use by just package importing
from . import (
    authentication_policy,
    authorization,
    session,
    user_groups
)

# import errors from modules to package scope
from .authentication_policy import AuthenticationError
from .authorization import (
    AuthorizationError,
    RegistrationError
)
