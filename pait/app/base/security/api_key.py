from abc import ABCMeta
from typing import Callable, Optional, Union

from any_api.openapi.model.openapi import security

from pait.field import Cookie, Header, Query

from .base import BaseSecurity
from .util import set_and_check_field

APIKEY_FIELD_TYPE = Union[Query, Header, Cookie]


class BaseAPIKey(BaseSecurity, metaclass=ABCMeta):
    def __init__(
        self,
        *,
        name: str,
        field: APIKEY_FIELD_TYPE,
        verify_api_key_callable: Optional[Callable[[str], bool]] = None,
        security_name: Optional[str] = None,
    ) -> None:
        field_name: str = field.get_field_name()
        if field_name not in ("query", "header", "cookie"):
            raise ValueError(f"APIKey not support {field}")
        self.not_authenticated_exc: Exception = self.get_exception(status_code=403, message="Not authenticated")
        set_and_check_field(field, name, self.not_authenticated_exc)

        self.verify_api_key_callable: Optional[Callable[[str], bool]] = verify_api_key_callable
        self.model: security.ApiKeySecurityModel = security.ApiKeySecurityModel(
            name=name, in_stub=field_name  # type: ignore
        )
        self.security_name = security_name or self.__class__.__name__

        def __call__(authorization: str = field) -> str:
            return self.authorization_handler(authorization)

        self._override_call_sig(__call__)

    def __call__(self, authorization: str = Header.i()) -> Optional[str]:
        return self.authorization_handler(authorization)

    def authorization_handler(self, authorization: str) -> str:
        if self.verify_api_key_callable and not self.verify_api_key_callable(authorization):
            raise self.not_authenticated_exc
        return authorization
