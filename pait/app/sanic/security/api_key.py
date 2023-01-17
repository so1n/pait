from abc import ABCMeta
from typing import Callable, Optional, Type

from sanic.exceptions import SanicException

from pait.app.base.security.api_key import APIKEY_FIELD_TYPE
from pait.app.base.security.api_key import APIkey as BaseAPIKey
from pait.app.base.security.api_key import api_key as _api_key


class APIKey(BaseAPIKey, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str) -> Exception:
        return SanicException(message=message, status_code=status_code)


def api_key(
    *,
    name: str,
    field: APIKEY_FIELD_TYPE,
    verify_api_key_callable: Callable[[str], bool],
    security_name: Optional[str] = None,
    api_key_class: Type[BaseAPIKey] = APIKey,
) -> BaseAPIKey:
    return _api_key(
        name=name,
        api_key_class=api_key_class,
        field=field,
        verify_api_key_callable=verify_api_key_callable,
        security_name=security_name,
    )
