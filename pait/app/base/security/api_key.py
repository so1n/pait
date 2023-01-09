from abc import ABCMeta
from typing import Callable, Optional, Type, Union

from any_api.openapi.model.openapi import security

from pait.field import Cookie, Header, Query

from .base import BaseSecurity

APIKEY_FIELD_TYPE = Type[Union[Query, Header, Cookie]]


class APIkey(BaseSecurity, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str) -> Exception:
        return NotImplementedError()


def api_key(
    *,
    name: str,
    api_key_class: Type[APIkey],
    field: APIKEY_FIELD_TYPE,
    verify_api_key_callable: Callable[[str], bool],
    security_name: Optional[str] = None,
) -> APIkey:
    class _APIKey(api_key_class):  # type: ignore
        def __init__(self) -> None:
            field_name: str = field.get_field_name()
            if field_name not in ("query", "header", "cookie"):
                raise ValueError(f"APIKey not support {field}")
            self.model: security.ApiKeySecurityModel = security.ApiKeySecurityModel(
                name=name, in_stub=field_name  # type: ignore
            )
            self.security_name = security_name or self.__class__.__name__

        def __call__(
            self,
            api_key: str = field.i(
                default="", alias=name, example="This value is a placeholder, please use the Authorize"
            ),
        ) -> Optional[str]:
            if not verify_api_key_callable(api_key):
                raise self.get_exception(status_code=403, message="Not authenticated")
            return api_key

    return _APIKey()
