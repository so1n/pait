from abc import ABCMeta

from pait.app.base.security.oauth2 import (
    BaseOAuth2PasswordBearer,
    BaseOAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFromStrict,
    oauth_2_password_bearer,
)
from pait.util import partial_wrapper

from .util import GetException

__all__ = [
    "OAuth2PasswordBearer",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "BaseOAuth2PasswordRequestFrom",
]


class OAuth2PasswordBearer(GetException, BaseOAuth2PasswordBearer, metaclass=ABCMeta):
    pass


oauth_2_password_bearer = partial_wrapper(oauth_2_password_bearer, class_=OAuth2PasswordBearer)
