from abc import ABCMeta

from starlette.exceptions import HTTPException

from pait.app.base.security.api_key import APIkey as BaseAPIKey
from pait.app.base.security.api_key import api_key as _api_key
from pait.util import partial_wrapper


class APIKey(BaseAPIKey, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str) -> Exception:
        return HTTPException(status_code=status_code, detail=message)


api_key = partial_wrapper(_api_key, api_key_class=APIKey)
