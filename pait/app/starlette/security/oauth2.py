from abc import ABCMeta
from typing import Dict, Optional

from starlette.exceptions import HTTPException

from pait.app.base.security.oauth2 import (
    BaseOAuth2PasswordBearer,
    BaseOAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFromStrict,
    oauth_2_password_bearer,
)
from pait.util import partial_wrapper

__all__ = [
    "OAuth2PasswordBearer",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "BaseOAuth2PasswordRequestFrom",
]


class OAuth2PasswordBearer(BaseOAuth2PasswordBearer, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        # starlette not support read header from exc
        return HTTPException(status_code=status_code, detail=message)


oauth_2_password_bearer = partial_wrapper(oauth_2_password_bearer, class_=OAuth2PasswordBearer)
