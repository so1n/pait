from abc import ABCMeta
from typing import Callable, Optional, Type

from werkzeug.exceptions import HTTPException

from pait.app.base.security.api_key import APIKEY_FIELD_TYPE
from pait.app.base.security.api_key import APIkey as BaseAPIKey
from pait.app.base.security.api_key import LinksModel
from pait.app.base.security.api_key import api_key as _api_key


class APIkey(BaseAPIKey, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str) -> Exception:
        exc = HTTPException(description=message)
        exc.code = status_code
        return exc


def api_key(
    *,
    name: str,
    field: APIKEY_FIELD_TYPE,
    verify_api_key_callable: Callable[[str], bool],
    security_name: Optional[str] = None,
    api_key_class: Type[BaseAPIKey] = APIkey,
    links: "Optional[LinksModel]" = None,
) -> BaseAPIKey:
    return _api_key(
        name=name,
        api_key_class=api_key_class,
        field=field,
        links=links,
        verify_api_key_callable=verify_api_key_callable,
        security_name=security_name,
    )
