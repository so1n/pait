import difflib
import json
import random
import sys
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Callable, Type
from unittest import mock

import pytest
from redis import Redis  # type: ignore
from tornado.testing import AsyncHTTPTestCase, HTTPResponse
from tornado.web import Application

from example.param_verify import tornado_example
from pait.api_doc.html import get_redoc_html, get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenAPI
from pait.app import auto_load_app, get_app_attribute, set_app_attribute
from pait.app.tornado import TestHelper as _TestHelper
from pait.app.tornado import load_app
from pait.model import response
from tests.conftest import enable_plugin, grpc_test_create_user_request, grpc_test_openapi
from tests.test_app.base_test import BaseTest

if TYPE_CHECKING:
    pass


class BaseTestTornado(AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return tornado_example.create_app()

    @property
    def base_test(self) -> BaseTest:
        return BaseTest(self, _TestHelper)

    def get_url(self, path: str) -> str:
        """Returns an absolute url for the given path on the test server."""
        return "%s://localhost:%s%s" % (self.get_protocol(), self.get_http_port(), path)


class TestTornado(BaseTestTornado):
    def response_test_helper(
        self, route_handler: Callable, pait_response: Type[response.PaitBaseResponseModel]
    ) -> None:
        from pait.app.tornado.plugin.mock_response import AsyncMockPlugin

        test_helper: _TestHelper = _TestHelper(self, route_handler)
        test_helper.get()

        with enable_plugin(route_handler, AsyncMockPlugin.build()):
            resp: HTTPResponse = test_helper.get()
            for key, value in pait_response.header.items():
                assert resp.headers[key] == value
            if issubclass(pait_response, response.PaitHtmlResponseModel) or issubclass(
                pait_response, response.PaitTextResponseModel
            ):
                assert resp.body.decode() == pait_response.get_example_value()
            else:
                assert resp.body == pait_response.get_example_value()

    def test_post(self) -> None:
        test_helper: _TestHelper = _TestHelper(
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
            resp: dict = json.loads(self.fetch(url).body.decode())
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_text_response(self) -> None:
        self.response_test_helper(tornado_example.TextResponseHanler.get, response.PaitTextResponseModel)

    def test_html_response(self) -> None:
        self.response_test_helper(tornado_example.HtmlResponseHanler.get, response.PaitHtmlResponseModel)

    def test_file_response(self) -> None:
        self.response_test_helper(tornado_example.FileResponseHanler.get, response.PaitFileResponseModel)

    def test_doc_route(self) -> None:
        tornado_example.add_api_doc_route(self._app)
        assert self.fetch("/swagger").code == 404
        assert self.fetch("/redoc").code == 404
        assert self.fetch("/swagger?pin_code=6666").body.decode() == get_swagger_ui_html(
            self.get_url("/openapi.json?pin_code=6666"), "Pait Api Doc(private)"
        )
        assert self.fetch("/redoc?pin_code=6666").body.decode() == get_redoc_html(
            self.get_url("/openapi.json?pin_code=6666"), "Pait Api Doc(private)"
        )
        assert (
            json.loads(self.fetch("/openapi.json?pin_code=6666&template-token=xxx").body.decode())["paths"][
                "/api/user"
            ]["get"]["parameters"][0]["schema"]["example"]
            == "xxx"
        )
        assert (
            difflib.SequenceMatcher(
                None,
                str(json.loads(self.fetch("/openapi.json?pin_code=6666").body.decode())),
                str(
                    PaitOpenAPI(
                        load_app(self.get_app()),
                        title="Pait Api Doc(private)",
                        open_api_server_list=[{"url": "http://localhost", "description": ""}],
                    ).open_api_dict
                ),
            ).quick_ratio()
            > 0.95
        )

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import tornado

        with mock.patch.dict("sys.modules", sys.modules):
            assert tornado == auto_load_app.auto_load_app_class()

    def test_app_attribute(self) -> None:
        key: str = "test_app_attribute"
        value: int = random.randint(1, 100)
        app: Application = self.get_app()
        set_app_attribute(app, key, value)
        assert get_app_attribute(app, key) == value

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
            } == _TestHelper(
                self,
                tornado_example.PaitBaseFieldHandler.post,
                file_dict={f1.name: f1.read()},
                form_dict={"a": "1", "b": "2", "c": "3"},
                cookie_dict={"abcd": "abcd"},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                path_dict={"age": 2},
                strict_inspection_check_json_content=False,
            ).json()

            # can not use get(Http Method) in form or file request
            with pytest.raises(RuntimeError):
                _TestHelper(
                    self,
                    tornado_example.PaitBaseFieldHandler.post,
                    file_dict={f1.name: f1.read()},
                    form_dict={"a": "1", "b": "2", "c": "3"},
                    cookie_dict={"cookie": "abcd=abcd;"},
                    query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                    path_dict={"age": 2},
                    strict_inspection_check_json_content=False,
                ).get()

    def test_raise_tip_route(self) -> None:
        self.base_test.raise_tip_route(tornado_example.RaiseTipHandler.post)

    def test_auto_complete_json_route(self) -> None:
        self.base_test.auto_complete_json_route(tornado_example.AutoCompleteJsonHandler.get)

    def test_same_alias_name(self) -> None:
        self.base_test.same_alias_name(tornado_example.SameAliasHandler.get)

    def test_field_default_factory_route(self) -> None:
        self.base_test.field_default_factory_route(tornado_example.FieldDefaultFactoryHandler.post)

    def test_check_param(self) -> None:
        self.base_test.check_param(tornado_example.CheckParamHandler.get)

    def test_check_response(self) -> None:
        self.base_test.check_response(tornado_example.CheckRespHandler.get)

    def test_mock_route(self) -> None:
        self.base_test.mock_route(tornado_example.MockHandler.get, tornado_example.UserSuccessRespModel2)

    def test_pait_model(self) -> None:
        self.base_test.pait_model(tornado_example.PaitModelHanler.post)

    def test_depend_route(self) -> None:
        self.base_test.depend_route(tornado_example.DependHandler.post)

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        self.base_test.depend_contextmanager(
            tornado_example.DependContextmanagerHanler.get,
            info_logger=info_logger,
            error_logger=error_logger,
        )

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        self.base_test.depend_contextmanager(
            tornado_example.DependAsyncContextmanagerHanler.get,
            info_logger=info_logger,
            error_logger=error_logger,
        )

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_pre_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        self.base_test.pre_depend_contextmanager(
            tornado_example.PreDependContextmanagerHanler.get,
            info_logger=info_logger,
            error_logger=error_logger,
        )

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_pre_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        self.base_test.pre_depend_contextmanager(
            tornado_example.PreDependAsyncContextmanagerHanler.get,
            info_logger=info_logger,
            error_logger=error_logger,
        )

    def test_get_cbv(self) -> None:
        self.base_test.get_cbv(tornado_example.CbvHandler.get)

    def test_post_cbv(self) -> None:
        self.base_test.post_cbv(tornado_example.CbvHandler.post)

    def test_cache_response(self) -> None:
        self.base_test.cache_response(
            tornado_example.CacheResponseHandler.get,
            tornado_example.CacheResponse1Handler.get,
            key="CacheResponse",
            app="tornado",
        )

    def test_cache_other_response_type(self) -> None:
        tornado_example.CacheResponsePlugin.set_redis_to_app(self._app, tornado_example.Redis(decode_responses=True))
        self.base_test.cache_other_response_type(
            tornado_example.TextResponseHanler.get,
            tornado_example.HtmlResponseHanler.get,
            tornado_example.CacheResponsePlugin,
        )

    def test_cache_response_param_name(self) -> None:
        self.base_test.cache_response_param_name(
            tornado_example.PostHandler.post,
            tornado_example.CacheResponsePlugin,
            tornado_example.Redis(decode_responses=True),
        )


class TestTornadoGrpc(BaseTestTornado):
    def test_create_user(self) -> None:
        tornado_example.add_grpc_gateway_route(self._app)
        tornado_example.add_api_doc_route(self._app)

        self._app.settings["before_server_start"]()

        def _(request_dict: dict) -> None:
            body: bytes = self.fetch("/api/user/create", body=json.dumps(request_dict).encode(), method="POST").body
            assert body == b"{}"

        grpc_test_create_user_request(self._app, _)

    def test_grpc_openapi(self) -> None:
        tornado_example.add_grpc_gateway_route(self._app)

        from pait.app.tornado import load_app

        grpc_test_openapi(load_app(self._app))

    def test_grpc_openapi_by_protobuf_file(self) -> None:
        from pait.app.tornado import load_app
        from pait.app.tornado.grpc_route import GrpcGatewayRoute

        self.base_test.grpc_openapi_by_protobuf_file(self._app, GrpcGatewayRoute, load_app)
