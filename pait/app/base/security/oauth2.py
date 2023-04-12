from typing import Any, Callable, Dict, Generator, List, Optional, Type

from any_api.openapi.model.openapi import Oauth2SecurityModel, OAuthFlowModel, OAuthFlowsModel
from pydantic import BaseModel, Field

from pait.field import Form, Header
from pait.model import JsonResponseModel, PaitCoreModel, get_core_model

from .base import BaseSecurity, SecurityModelType
from .util import get_authorization_scheme_param, set_and_check_field

__all__ = [
    "BaseOAuth2PasswordBearer",
    "BaseOAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "OAuth2PasswordBearerJsonRespModel",
]


class ScopeType(List[str]):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> List[str]:
        return v.split(" ")


class BaseOAuth2PasswordRequestFrom(BaseModel):
    username: str = Form()
    password: str = Form()
    scope: ScopeType = Form("")
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
        *,
        route: Optional[Callable] = None,
        security_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        header_field: Optional[Header] = None,
    ):
        self._model: Optional[SecurityModelType] = None

        self.route: Optional[Callable] = route
        self.security_name = security_name or self.__class__.__name__
        self.scopes: Dict[str, str] = scopes or {}
        self.header_field: Header = header_field or Header.i(openapi_include=False)

        if route:
            self.with_route(route)

        # init field
        self.not_authenticated_exc: Exception = self.get_exception(
            status_code=401, message="Not authenticated", headers={"WWW-Authenticate": "Bearer"}
        )
        set_and_check_field(self.header_field, "Authorization", self.not_authenticated_exc)

        def __call__(authorization: str = self.header_field) -> str:
            return self.authorization_handler(authorization)

        self._override_call_sig(__call__)

    def with_route(self, route: Callable) -> "BaseOAuth2PasswordBearer":
        if self.route is not None:
            raise ValueError("route has been set")
        self.route = route
        core_model: PaitCoreModel = get_core_model(route)
        self._set_model(core_model.path, self.scopes)

        def _set_model_by_core_model_change(*args: Any) -> None:
            self._set_model(core_model.path, self.scopes)

        core_model.add_change_notify(_set_model_by_core_model_change)
        return self

    def _set_model(self, path: str, scopes: Dict[str, str]) -> None:
        self._model = Oauth2SecurityModel(flows=OAuthFlowsModel(password=OAuthFlowModel(tokenUrl=path, scopes=scopes)))

    @property
    def model(self) -> SecurityModelType:
        if self._model is None:
            raise ValueError("The model is invalid, please use the `with_route` method to set the routing function")
        return self._model

    def __call__(self, authorization: str = Header.i()) -> str:
        return self.authorization_handler(authorization)

    def authorization_handler(self, authorization: str) -> str:
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise self.not_authenticated_exc
        return param
