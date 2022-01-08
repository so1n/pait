import json
import sys
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Generator, Type
from unittest import mock

import pytest
from tornado.testing import AsyncHTTPTestCase, HTTPResponse
from tornado.web import Application

from example.param_verify import tornado_example
from pait.app import auto_load_app
from pait.app.tornado import TornadoTestHelper
from pait.model import response
from tests.conftest import enable_mock


@pytest.fixture
def app() -> Generator[Application, None, None]:
    yield tornado_example.create_app()


class TestTornado(AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return tornado_example.create_app()

    def get_url(self, path: str) -> str:
        """Returns an absolute url for the given path on the test server."""
        return "%s://localhost:%s%s" % (self.get_protocol(), self.get_http_port(), path)

    def response_test_helper(
        self, route_handler: Callable, pait_response: Type[response.PaitBaseResponseModel]
    ) -> None:
        from pait.app.tornado.plugin.mock_response import MockPlugin

        test_helper: TornadoTestHelper = TornadoTestHelper(self, route_handler)
        test_helper.get()

        with enable_mock(route_handler, MockPlugin):
            resp: HTTPResponse = test_helper.get()
            for key, value in pait_response.header.items():
                assert resp.headers[key] == value
            if issubclass(pait_response, response.PaitHtmlResponseModel) or issubclass(
                pait_response, response.PaitTextResponseModel
            ):
                assert resp.body.decode() == pait_response.get_example_value()
            else:
                assert resp.body == pait_response.get_example_value()

    def test_raise_tip_route(self) -> None:
        msg: str = TornadoTestHelper(
            self, tornado_example.RaiseTipHandler.post, header_dict={"Content-Type": "test"}, body_dict={"temp": None}
        ).json()["msg"]
        assert 'File "/home/so1n/github/pait/example/param_verify/tornado_example.py", ' in msg
        assert "in post. error:content_type value is <class 'pydantic.fields.UndefinedType'>" in msg

    def test_post(self) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            tornado_example.PostHandler.post,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        response: HTTPResponse = self.fetch(
            "/api/post",
            headers={"user-agent": "customer_agent"},
            method="POST",
            body='{"uid": 123, "user_name": "appl", "age": 2, "sex": "man"}',
        )
        for resp_dict in [test_helper.json(), json.loads(response.body.decode())]:
            assert resp_dict["code"] == 0
            assert resp_dict["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/x-www-form-urlencoded",
                "sex": "man",
            }

    def test_check_json_route(self) -> None:
        for url, api_code in [
            (
                "/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10", -1),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            assert json.loads(self.fetch(url).body.decode())["code"] == api_code

    def test_same_alias_name(self) -> None:
        assert (
            TornadoTestHelper(
                self,
                tornado_example.SameAliasHandler.get,
                query_dict={"token": "query"},
                header_dict={"token": "header"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        )
        assert (
            TornadoTestHelper(
                self,
                tornado_example.SameAliasHandler.get,
                query_dict={"token": "query1"},
                header_dict={"token": "header1"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query1", "header_token": "header1"}}
        )

    def test_pait_base_field_route(self) -> None:
        file_content: str = "Hello Word!"

        with NamedTemporaryFile(delete=True) as f1:
            f1.write(file_content.encode())
            f1.seek(0)
            assert {
                "code": 0,
                "data": {
                    "age": 2,
                    "content": "Hello Word!",
                    "cookie": {"abcd": "abcd"},
                    "email": "example@xxx.com",
                    "filename": f1.name,
                    "form_a": "1",
                    "form_b": "2",
                    "form_c": ["3"],
                    "multi_user_name": ["abc", "efg"],
                    "sex": "man",
                    "uid": 123,
                    "user_name": "appl",
                },
                "msg": "",
            } == TornadoTestHelper(
                self,
                tornado_example.PaitBaseFieldHandler.post,
                file_dict={f1.name: f1.read()},
                form_dict={"a": "1", "b": "2", "c": "3"},
                cookie_dict={"cookie": "abcd=abcd;"},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                path_dict={"age": 2},
                strict_inspection_check_json_content=False,
            ).json()

    def test_check_param(self) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            tornado_example.CheckParamHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
        )
        assert "requires at most one of param user_name or alias_user_name" in test_helper.json()["msg"]
        test_helper = TornadoTestHelper(
            self,
            tornado_example.CheckParamHandler.get,
            query_dict={"uid": 123, "sex": "man", "age": 10, "alias_user_name": "appe"},
        )
        assert "birthday requires param alias_user_name, which if not none" in test_helper.json()["msg"]

    def test_check_response(self) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            tornado_example.CheckRespHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            test_helper.json()
        test_helper = TornadoTestHelper(
            self,
            tornado_example.CheckRespHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        test_helper.json()

    def test_mock_route(self) -> None:
        assert (
            TornadoTestHelper(
                self,
                tornado_example.MockHandler.get,
                path_dict={"age": 3},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
            ).json()
            == json.loads(tornado_example.UserSuccessRespModel2.get_example_value())
        )

    def test_pait_model(self) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {
                "uid": 123,
                "user_agent": "customer_agent",
                "user_info": {"age": 2, "user_name": "appl"},
            },
        } == TornadoTestHelper(
            self,
            tornado_example.PaitModelHanler.post,
            header_dict={"user-agent": "customer_agent"},
            query_dict={"uid": 123, "user_name": "appl"},
            body_dict={"user_info": {"age": 2, "user_name": "appl"}},
            strict_inspection_check_json_content=False,
        ).json()

    def test_depend(self) -> None:
        assert {"code": 0, "msg": "", "data": {"age": 2, "user_agent": "customer_agent"}} == TornadoTestHelper(
            self,
            tornado_example.DependHandler.post,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json()

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_pre_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            tornado_example.PreDependContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = TornadoTestHelper(
            self,
            tornado_example.PreDependContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_pre_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            tornado_example.PreDependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = TornadoTestHelper(
            self,
            tornado_example.PreDependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            tornado_example.DependContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = TornadoTestHelper(
            self,
            tornado_example.DependContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            tornado_example.DependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = TornadoTestHelper(
            self,
            tornado_example.DependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_get_cbv(self) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == TornadoTestHelper(
            self,
            tornado_example.CbvHandler.get,
            query_dict={"uid": "123", "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"Content-Type": "application/json"},
        ).json()

    def test_post_cbv(self) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == TornadoTestHelper(
            self,
            tornado_example.CbvHandler.post,
            body_dict={"uid": "123", "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"Content-Type": "application/json"},
        ).json()

    def test_text_response(self) -> None:
        self.response_test_helper(tornado_example.TextResponseHanler.get, response.PaitTextResponseModel)

    def test_html_response(self) -> None:
        self.response_test_helper(tornado_example.HtmlResponseHanler.get, response.PaitHtmlResponseModel)

    def test_file_response(self) -> None:
        self.response_test_helper(tornado_example.FileResponseHanler.get, response.PaitFileResponseModel)

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import tornado

        with mock.patch.dict("sys.modules", sys.modules):
            assert tornado == auto_load_app.auto_load_app_class()
