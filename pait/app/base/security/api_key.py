from abc import ABCMeta
from typing import Callable, Optional, Type, Union

from any_api.openapi.model.openapi import security

from pait.field import Cookie, Header, Query

from .base import BaseSecurity

APIKEY_FIELD_TYPE = Union[Query, Header, Cookie]


class BaseAPIKey(BaseSecurity, metaclass=ABCMeta):
    pass


def api_key(
    *,
    name: str,
    field: APIKEY_FIELD_TYPE,
    api_key_class: Type[BaseAPIKey] = BaseAPIKey,
    verify_api_key_callable: Callable[[str], bool],
    security_name: Optional[str] = None,
) -> BaseAPIKey:
    not_authenticated_exc: Exception = api_key_class.get_exception(status_code=403, message="Not authenticated")
    if field.alias is not None:
        raise ValueError("Custom alias parameters are not allowed")
    if field.not_value_exception is not None:
        raise ValueError("Custom not_value_exception parameters are not allowed")
    field.set_alias(name)
    field.not_value_exception = not_authenticated_exc

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
            api_key_: str = field,
        ) -> Optional[str]:
            if not verify_api_key_callable(api_key_):
                raise not_authenticated_exc
            return api_key_

    return _APIKey()
