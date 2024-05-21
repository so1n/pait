from typing import Type

from pait.app.base.security.oauth2 import (
    BaseOAuth2PasswordBearer,
    BaseOAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFromStrict,
)

from .util import get_security

__all__ = [
    "OAuth2PasswordBearer",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "BaseOAuth2PasswordRequestFrom",
]

OAuth2PasswordBearer: Type[BaseOAuth2PasswordBearer] = get_security("OAuth2PasswordBearer", "oauth2")
