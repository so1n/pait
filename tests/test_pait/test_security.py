from base64 import b64encode

import pytest

from pait.app.base import BaseAppHelper
from pait.app.base.security import api_key, http, oauth2, util
from pait.core import Pait
from pait.field import BaseRequestResourceField, Header


class TestAPIKey:
    def test_use_erroe_field(self) -> None:
        with pytest.raises(ValueError):
            api_key.BaseAPIKey(name="test", field=BaseRequestResourceField)  # type: ignore[arg-type]

    def test_authorization_handler(self) -> None:
        with pytest.raises(NotImplementedError):
            assert not api_key.BaseAPIKey(
                name="test", field=Header.i(), verify_api_key_callable=lambda x: bool(x)
            ).authorization_handler("")


class TestHttpBasic:
    def test_error_scheme(self) -> None:
        with pytest.raises(ValueError):
            http.BaseHTTPBasic(security_model=http.HttpSecurityModel(scheme="test"))

    def test_authorization_handler(self) -> None:
        with pytest.raises(NotImplementedError):
            http.BaseHTTPBasic().authorization_handler("test")

        assert http.BaseHTTPBasic(is_raise=False).authorization_handler("test") is None

        # ({"Authorization": f"Basic so1n:so1n"}, 401),  # can not decode
        # ({"Authorization": f"Basic {b64encode(b'so1n:').decode()}"}, 401),  # not pw

        # test decode error
        with pytest.raises(NotImplementedError):
            http.BaseHTTPBasic().authorization_handler("Basic test")
        # test partition error
        with pytest.raises(NotImplementedError):
            http.BaseHTTPBasic().authorization_handler(f"Basic {b64encode(b'so1n').decode()}")
        http_basic_credentials = http.BaseHTTPBasic().authorization_handler(f"Basic {b64encode(b'so1n:so1n').decode()}")
        assert http_basic_credentials
        assert http_basic_credentials.username == "so1n"
        assert http_basic_credentials.password == "so1n"


class DemoPait(Pait):
    app_helper_class = BaseAppHelper


_pait = DemoPait()


@_pait()
def demo() -> None:
    pass


class TestOAuth2PasswordBaere:
    def test_with_route(self) -> None:
        oauth2_pb = oauth2.BaseOAuth2PasswordBearer(route=demo)
        with pytest.raises(ValueError) as e:
            oauth2_pb.with_route(demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("route has been set")

    def test_not_use_route(self) -> None:
        with pytest.raises(ValueError) as e:
            oauth2.BaseOAuth2PasswordBearer().model
        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith(
            "The model is invalid, please use the `with_route` method to set the routing function"
        )

        with pytest.raises(ValueError) as e:
            oauth2.BaseOAuth2PasswordBearer().get_depend()

        exec_msg = e.value.args[0]
        assert exec_msg.startswith(
            "The model is invalid, please use the `with_route` method to set the routing function"
        )

    def test_use_scopes(self) -> None:
        oauth2_pb = oauth2.BaseOAuth2PasswordBearer(route=demo, scopes={"a": "", "b": ""})
        assert oauth2_pb.get_depend(use_scopes=["a"]).is_allow(["a"])
        assert not oauth2_pb.get_depend(use_scopes=["a"]).is_allow(["b"])
        assert oauth2_pb.get_depend(use_scopes=["a", "b"]).is_allow(["b"])
        assert not oauth2_pb.get_depend(use_scopes=["a", "b"]).is_allow(["c"])

    def test_authorization_handler(self) -> None:
        oauth2_pb = oauth2.BaseOAuth2PasswordBearer(route=demo, scopes={"a": "", "b": ""})
        with pytest.raises(NotImplementedError):
            oauth2_pb.get_depend().authorization_handler(f"Basic {b64encode(b'so1n').decode()}")


class TestUtil:
    def test_set_and_check_field(self) -> None:
        header = Header.i()
        exc = RuntimeError("abc")
        util.set_and_check_field(header, "aaa", exc)
        assert header.alias == "aaa"
        assert header.not_value_exception_func("") == exc

        with pytest.raises(ValueError):
            util.set_and_check_field(Header.i(alias="demo"), "aaa")
        with pytest.raises(ValueError):
            util.set_and_check_field(Header.i(not_value_exception_func=lambda x: ValueError(0)), "aaa")

    def test_get_authorization_scheme_param(self) -> None:
        assert util.get_authorization_scheme_param("") == ("", "")
        assert util.get_authorization_scheme_param("a b") == ("a", "b")
