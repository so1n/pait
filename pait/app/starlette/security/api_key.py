from abc import ABCMeta
from typing import Dict, Optional

from starlette.exceptions import HTTPException

from pait.app.base.security.api_key import BaseAPIKey as BaseAPIKey
from pait.app.base.security.api_key import api_key as _api_key
from pait.util import partial_wrapper


class APIKey(BaseAPIKey, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        # starlette not support read header from exc
        return HTTPException(status_code=status_code, detail=message)


api_key = partial_wrapper(_api_key, api_key_class=APIKey)
