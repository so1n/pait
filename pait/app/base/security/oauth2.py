from typing import Any, Callable, Dict, List, Optional, Type

from any_api.openapi.model.openapi import Oauth2SecurityModel, OAuthFlowModel, OAuthFlowsModel
from any_api.openapi.model.openapi.security import UserScopesOauth2SecurityModel
from pydantic import BaseModel, Field

from pait import _pydanitc_adapter
from pait.field import Form, Header
from pait.model.core import PaitCoreModel, get_core_model
from pait.model.response import JsonResponseModel

from .base import BaseSecurity, SecurityModelType
from .util import get_authorization_scheme_param, set_and_check_field

__all__ = [
    "BaseOAuth2PasswordBearer",
    "BaseOAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "OAuth2PasswordBearerJsonRespModel",
]


class BaseOAuth2PasswordRequestFrom(BaseModel):
    username: str = Form()
    password: str = Form()
    scope: List[str] = Form(default_factory=list)
    client_id: Optional[str] = Form(None)
    client_secret: Optional[str] = Form(None)

    @_pydanitc_adapter.model_validator(mode="before")
    def _post_init(cls, value: dict) -> dict:
        scope = value.get("scope", "")
        if isinstance(scope, str):
            value["scope"] = scope.split(" ")
        return value


class OAuth2PasswordRequestFrom(BaseOAuth2PasswordRequestFrom):
    grant_type: Optional[str] = Form(None, regex="password")


class OAuth2PasswordRequestFromStrict(BaseOAuth2PasswordRequestFrom):
    grant_type: str = Form(regex="password")


class OAuth2PasswordBearerJsonRespModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        access_token: str = Field(description="")
        token_type: str = Field(default="bearer")

    response_data: Type[BaseModel] = ResponseModel


class BaseOAuth2PasswordBearerProxy(BaseSecurity):
    def __init__(self, *, security: "BaseOAuth2PasswordBearer", use_scopes: Optional[List[str]] = None):
        self.security = security
        self.use_scopes = use_scopes
        self.security_name = security.security_name

        def pait_handler(authorization: str = security.header_field) -> str:
            return self.authorization_handler(authorization)

        self.set_pait_handler(pait_handler)

    def __call__(self, authorization: str = Header.i()) -> str:
        raise RuntimeError("should not call this method")  # pragma: no cover

    @property
    def model(self) -> SecurityModelType:
        if self.use_scopes:
            return UserScopesOauth2SecurityModel(
                use_scopes=self.use_scopes, model=self.security.model, flows=self.security.model.flows
            )
        return self.security.model

    def is_allow(self, scopes: List[str]) -> bool:
        return len(set(scopes) & set(self.model.get_security_scope())) > 0

    def authorization_handler(self, authorization: str) -> str:
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise self.security.not_authenticated_exc
        return param


class BaseOAuth2PasswordBearer(BaseSecurity):
    _proxy = BaseOAuth2PasswordBearerProxy

    def __init__(
        self,
        *,
        route: Optional[Callable] = None,
        security_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        header_field: Optional[Header] = None,
    ):
        self._model: Optional[SecurityModelType] = None
        self._scopes: Dict[str, str] = scopes or {}

        self.route: Optional[Callable] = None
        self.security_name = security_name or self.__class__.__name__
        self.header_field: Header = header_field or Header.i(openapi_include=False)

        if route:
            self.with_route(route)

        # init field
        self.not_authenticated_exc: Exception = self.get_exception(
            status_code=401, message="Not authenticated", headers={"WWW-Authenticate": "Bearer"}
        )
        set_and_check_field(self.header_field, "Authorization", self.not_authenticated_exc)

    def with_route(self, route: Callable) -> "BaseOAuth2PasswordBearer":
        if self.route is not None:
            raise ValueError("route has been set")
        self.route = route
        core_model: PaitCoreModel = get_core_model(route)
        self._set_model(core_model.path)

        def _set_model_by_core_model_change(*args: Any) -> None:
            self._set_model(core_model.path)

        core_model.add_change_notify(_set_model_by_core_model_change)
        return self

    def _set_model(self, path: str) -> None:
        self._model = Oauth2SecurityModel(
            flows=OAuthFlowsModel(password=OAuthFlowModel(tokenUrl=path, scopes=self._scopes))
        )

    @property
    def model(self) -> SecurityModelType:
        if self._model is None:
            raise ValueError("The model is invalid, please use the `with_route` method to set the routing function")
        return self._model

    def get_depend(self, use_scopes: Optional[List[str]] = None) -> "BaseOAuth2PasswordBearerProxy":
        self.model  # It is only used to check whether a route is bound
        return self._proxy(
            security=self,
            use_scopes=use_scopes,
        )
