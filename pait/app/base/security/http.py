import binascii
import warnings
from base64 import b64decode
from typing import Callable, Optional

from any_api.openapi.model.openapi.security import HttpSecurityModel
from pydantic import BaseModel

from pait.field import Header

from .base import BaseSecurity
from .util import get_authorization_scheme_param, set_and_check_field


class HTTPBasicCredentials(BaseModel):
    username: str
    password: str
    realm: Optional[str] = None


class BaseHTTPBasic(BaseSecurity):
    def __init__(
        self,
        *,
        security_model: HttpSecurityModel = HttpSecurityModel(scheme="basic"),
        security_name: Optional[str] = None,
        header_field: Optional[Header] = None,
        realm: Optional[str] = None,
        is_raise: bool = True,
    ) -> None:
        """
        :param security_model: http basic auth security model
        :param security_name: name of http basic auth security model in openapi spec
        :param header_field: pait header field
        :param realm: realm of http basic auth security model
        :param is_raise: is raise exception if there is invalid http basic auth data

        Note: If the validation fails and 'is raise' is true, only a 401 exception will be thrown,
            and if you want to throw a 403 exception, you need to handle it through inheritance or other methods
        """
        if security_model.scheme != "basic":
            raise ValueError(f"{self.__class__.__name__} only support basic scheme")  # pragma: no cover
        self.model = security_model
        self.is_raise: bool = is_raise
        self.security_name = security_name or self.__class__.__name__
        self.header_field: Header = header_field or Header.i(openapi_include=False)
        self.realm: Optional[str] = realm
        self.not_authorization_exc: Exception = self.get_exception(
            status_code=401,
            message="Not authentication",
            headers={"WWW-Authenticate": f'Basic realm="{realm}"'} if realm else {"WWW-Authenticate": "Basic"},
        )
        set_and_check_field(self.header_field, "Authorization", self.not_authorization_exc if is_raise else None)

        def pait_handler(authorization: str = self.header_field) -> Optional[HTTPBasicCredentials]:
            return self.authorization_handler(authorization)

        self.set_pait_handler(pait_handler)

    def __call__(self, authorization: str = Header.i()) -> Optional[HTTPBasicCredentials]:
        raise RuntimeError("should not call this method")  # pragma: no cover

    def authorization_handler(self, authorization: str) -> Optional[HTTPBasicCredentials]:
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or (scheme.lower() != "basic"):
            if self.is_raise:
                raise self.not_authorization_exc
            else:
                return None

        try:
            data = b64decode(param).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise self.not_authorization_exc
        username, separator, password = data.partition(":")
        if not separator:
            raise self.not_authorization_exc
        return HTTPBasicCredentials(username=username, password=password, realm=self.realm)


class BaseHTTP(BaseSecurity):
    def __init__(
        self,
        *,
        security_model: HttpSecurityModel,
        security_name: Optional[str] = None,
        header_field: Optional[Header] = None,
        is_raise: bool = True,
        verify_callable: Optional[Callable[[str], bool]] = None,
    ):
        """
        :param security_model: http basic auth security model
        :param security_name: name of http basic auth security model in openapi spec
        :param header_field: pait header field
        :param is_raise: is raise exception if there is invalid http basic auth data
        :param verify_callable: callable to verify http basic auth data
        """
        self.model: HttpSecurityModel = security_model
        self.security_name = security_name or self.__class__.__name__
        self.header_field: Header = header_field or Header.i(openapi_include=False)
        self.is_raise: bool = is_raise
        self.verify_callable: Optional[Callable[[str], bool]] = verify_callable

        self.not_authenticated_exc: Exception = self.get_exception(status_code=403, message="Not authenticated")
        set_and_check_field(self.header_field, "Authorization", self.not_authenticated_exc if is_raise else None)

        def pait_handler(authorization: str = self.header_field) -> Optional[str]:
            return self.authorization_handler(authorization)

        self.set_pait_handler(pait_handler)

    def __call__(self, authorization: str = Header.i()) -> Optional[str]:
        raise RuntimeError("should not call this method")  # pragma: no cover

    def authorization_handler(self, authorization: str) -> Optional[str]:
        scheme, credentials = get_authorization_scheme_param(authorization)
        if (not (authorization and scheme and credentials)) or (scheme.lower() != self.model.scheme):
            if self.is_raise:
                raise self.not_authenticated_exc
            else:
                return None
        if self.verify_callable and not self.verify_callable(authorization):
            raise self.not_authenticated_exc
        return credentials


class BaseHTTPBearer(BaseHTTP):
    def __init__(
        self,
        *,
        bearer_format: Optional[str] = None,
        security_name: Optional[str] = None,
        header_field: Optional[Header] = None,
        is_raise: bool = True,
        verify_callable: Optional[Callable[[str], bool]] = None,
    ):
        """
        :param bearer_format: 'Bearer' style token, 'Authorization: Bearer <token>'
        :param security_name: name of http basic auth security model in openapi spec
        :param header_field: pait header field
        :param is_raise: is raise exception if there is invalid http basic auth data
        :param verify_callable: callable to verify http basic auth data
        """
        super().__init__(
            security_model=HttpSecurityModel(scheme="bearer", bearerFormat=bearer_format),
            security_name=security_name,
            header_field=header_field,
            is_raise=is_raise,
            verify_callable=verify_callable,
        )


class BaseHTTPDigest(BaseHTTP):
    def __init__(
        self,
        security_name: Optional[str] = None,
        header_field: Optional[Header] = None,
        is_raise: bool = True,
        verify_callable: Optional[Callable[[str], bool]] = None,
    ) -> None:
        """
        :param security_name: name of http basic auth security model in openapi spec
        :param header_field: pait header field
        :param is_raise: is raise exception if there is invalid http basic auth data
        :param verify_callable: callable to verify http basic auth data
        """
        super().__init__(
            security_model=HttpSecurityModel(scheme="digest"),
            security_name=security_name,
            header_field=header_field,
            is_raise=is_raise,
            verify_callable=verify_callable,
        )

    def authorization_handler(self, authorization: str) -> Optional[str]:
        warnings.warn("Http Digest just a simple example and does not provide practical usage")
        return super().authorization_handler(authorization)
