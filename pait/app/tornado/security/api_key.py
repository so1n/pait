from abc import ABCMeta
from typing import Dict, Optional

from tornado.web import HTTPError

from pait.app.base.security.api_key import BaseAPIKey
from pait.app.base.security.api_key import api_key as _api_key
from pait.util import partial_wrapper


class APIKey(BaseAPIKey, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        # tornado not support read header from exc
        return HTTPError(status_code=status_code, reason=message)


api_key = partial_wrapper(_api_key, api_key_class=APIKey)
