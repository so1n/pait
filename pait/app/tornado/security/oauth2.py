from typing import Dict, Optional

from tornado.web import HTTPError

from pait.app.base.security.oauth2 import (
    BaseOAuth2PasswordBearer,
    BaseOAuth2PasswordRequestFrom,
    OAuth2PasswordBearerJsonRespModel,
    OAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFromStrict,
)

__all__ = [
    "OAuth2PasswordBearer",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "BaseOAuth2PasswordRequestFrom",
    "OAuth2PasswordBearerJsonRespModel",
]


class OAuth2PasswordBearer(BaseOAuth2PasswordBearer):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        # tornado not support read header from exc
        return HTTPError(status_code=status_code, reason=message)
