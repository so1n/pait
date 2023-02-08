from typing import Any, Callable, Dict, Optional, Tuple, Type

from any_api.openapi.model.openapi import Oauth2SecurityModel, OAuthFlowModel, OAuthFlowsModel
from pydantic import BaseModel, Field

from pait.field import Form, Header
from pait.model.core import PaitCoreModel, get_core_model
from pait.model.response import JsonResponseModel

from .base import BaseSecurity
from .util import set_and_check_field

__all__ = [
    "BaseOAuth2PasswordBearer",
    "BaseOAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "OAuth2PasswordBearerJsonRespModel",
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


class OAuth2PasswordBearerJsonRespModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        access_token: str = Field(description="")
        token_type: str = Field(default="bearer")

    response_data: Type[BaseModel] = ResponseModel


class BaseOAuth2PasswordBearer(BaseSecurity):
    def __init__(
        self,
        route: Callable,
        security_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        header_field: Optional[Header] = None,
    ):
        self.security_name = security_name or self.__class__.__name__

        # update model
        core_model: PaitCoreModel = get_core_model(route)
        self._set_model(core_model.path, scopes or {})

        def _set_model_by_core_model_change(*args: Any) -> None:
            self._set_model(core_model.path, scopes or {})

        core_model.add_change_notify(_set_model_by_core_model_change)

        # init field
        _header_field: Header = header_field or Header.i(openapi_include=False)
        self.not_authenticated_exc: Exception = self.get_exception(
            status_code=401, message="Not authenticated", headers={"WWW-Authenticate": "Bearer"}
        )
        set_and_check_field(_header_field, "Authorization", self.not_authenticated_exc)

        def __call__(authorization: str = _header_field) -> str:
            return self.authorization_handler(authorization)

        # Compatible with the following syntax
        # Oauth2PasswordBearer()()
        # Oauth2PasswordBearer().__call__()
        setattr(self, "_override_call_sig", True)
        setattr(self, "__call__", __call__)

    def _set_model(self, path: str, scopes: Dict[str, str]) -> None:
        self.model = Oauth2SecurityModel(flows=OAuthFlowsModel(password=OAuthFlowModel(tokenUrl=path, scopes=scopes)))

    def __call__(self, authorization: str = Header.i()) -> str:
        return self.authorization_handler(authorization)

    def authorization_handler(self, authorization: str) -> str:
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise self.not_authenticated_exc
        return param
