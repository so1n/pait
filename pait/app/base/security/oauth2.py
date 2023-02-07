from abc import ABCMeta
from typing import Any, Callable, Dict, Optional, Tuple, Type

from any_api.openapi.model.openapi import Oauth2SecurityModel, OAuthFlowModel, OAuthFlowsModel
from pydantic import BaseModel

from pait.field import Form, Header
from pait.model.core import PaitCoreModel, get_core_model

from .base import BaseSecurity

__all__ = [
    "BaseOAuth2PasswordBearer",
    "oauth_2_password_bearer",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "BaseOAuth2PasswordRequestFrom",
]


def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


class BaseOAuth2PasswordRequestFrom(BaseModel):
    username: str = Form()
    password: str = Form()
    scope: str = Form("")
    client_id: Optional[str] = Form(None)
    client_secret: Optional[str] = Form(None)


class OAuth2PasswordRequestFrom(BaseOAuth2PasswordRequestFrom):
    grant_type: Optional[str] = Form(None, regex="password")


class OAuth2PasswordRequestFromStrict(BaseOAuth2PasswordRequestFrom):
    grant_type: str = Form(regex="password")


class BaseOAuth2PasswordBearer(BaseSecurity, metaclass=ABCMeta):
    def __init__(
        self,
        route: Callable,
        security_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
    ):
        core_model: PaitCoreModel = get_core_model(route)

        self.security_name = security_name or self.__class__.__name__
        self._set_model(core_model.path, scopes or {})

        def _set_model_by_core_model_change(*args: Any) -> None:
            self._set_model(core_model.path, scopes or {})

        core_model.add_change_notify(_set_model_by_core_model_change)

    def _set_model(self, path: str, scopes: Dict[str, str]) -> None:
        self.model = Oauth2SecurityModel(flows=OAuthFlowsModel(password=OAuthFlowModel(tokenUrl=path, scopes=scopes)))


def oauth_2_password_bearer(
    *,
    route: Callable,
    class_: Type[BaseOAuth2PasswordBearer] = BaseOAuth2PasswordBearer,
    security_name: Optional[str] = None,
    scopes: Optional[Dict[str, str]] = None,
    header_field: Optional[Header] = None,
) -> BaseOAuth2PasswordBearer:
    _header_field: Header = header_field or Header.i(openapi_include=False)
    not_authenticated_exc: Exception = class_.get_exception(
        status_code=401, message="Not authenticated", headers={"WWW-Authenticate": "Bearer"}
    )
    if _header_field.alias is not None:
        raise ValueError("Custom alias parameters are not allowed")
    if _header_field.not_value_exception is not None:
        raise ValueError("Custom not_value_exception parameters are not allowed")
    _header_field.set_alias("Authorization")
    _header_field.not_value_exception = not_authenticated_exc

    class OAuth2PasswordBearer(class_):  # type: ignore
        def __call__(self, authorization: str = _header_field) -> Optional[str]:
            scheme, param = get_authorization_scheme_param(authorization)
            if not authorization or scheme.lower() != "bearer":
                raise self.get_exception(
                    status_code=401, message="Not authenticated", headers={"WWW-Authenticate": "Bearer"}
                )
            return param

    return OAuth2PasswordBearer(route=route, security_name=security_name, scopes=scopes)
