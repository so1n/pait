from pait.app.base.security.oauth2 import (
    BaseOAuth2PasswordBearer,
    BaseOAuth2PasswordRequestFrom,
    OAuth2PasswordBearerJsonRespModel,
    OAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFromStrict,
)

from .util import GetException

__all__ = [
    "OAuth2PasswordBearer",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "BaseOAuth2PasswordRequestFrom",
    "OAuth2PasswordBearerJsonRespModel",
]


class OAuth2PasswordBearer(GetException, BaseOAuth2PasswordBearer):
    pass
