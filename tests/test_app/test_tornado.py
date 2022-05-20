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

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class BaseTestTornado(AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return tornado_example.create_app()

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

    def test_raise_tip_route(self) -> None:
        msg: str = _TestHelper(
            self, tornado_example.RaiseTipHandler.post, header_dict={"Content-Type": "test"}, body_dict={"temp": None}
        ).json()["msg"]
        assert msg == "error param:content__type, Can not found content__type value"

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

    def test_auto_complete_json_route(self) -> None:
        test_helper: _TestHelper = _TestHelper(
            self,
            tornado_example.AutoCompleteJsonHandler.get,
        )
        resp_dict: dict = test_helper.json()
        assert resp_dict["data"]["uid"] == 100
        assert resp_dict["data"]["music_list"][1]["name"] == ""
        assert resp_dict["data"]["music_list"][1]["singer"] == ""

    def test_same_alias_name(self) -> None:
        assert (
            _TestHelper(
                self,
                tornado_example.SameAliasHandler.get,
                query_dict={"token": "query"},
                header_dict={"token": "header"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        )
        assert (
            _TestHelper(
                self,
                tornado_example.SameAliasHandler.get,
                query_dict={"token": "query1"},
                header_dict={"token": "header1"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query1", "header_token": "header1"}}
        )

    def test_field_default_factory_route(self) -> None:
        assert (
            _TestHelper(
                self,
                tornado_example.FieldDefaultFactoryHandler.post,
                body_dict={"demo_value": 0},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"demo_value": 0, "data_list": [], "data_dict": {}}}
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

    def test_check_param(self) -> None:
        test_helper: _TestHelper = _TestHelper(
            self,
            tornado_example.CheckParamHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert "requires at most one of param user_name or alias_user_name" in test_helper.json()["msg"]
        test_helper = _TestHelper(
            self,
            tornado_example.CheckParamHandler.get,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01"},
            strict_inspection_check_json_content=False,
        )
        assert "birthday requires param alias_user_name, which if not none" in test_helper.json()["msg"]
        test_helper = _TestHelper(
            self,
            tornado_example.CheckParamHandler.get,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01", "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert test_helper.json()["code"] == 0

    def test_check_response(self) -> None:
        test_helper: _TestHelper = _TestHelper(
            self,
            tornado_example.CheckRespHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            test_helper.json()
        test_helper = _TestHelper(
            self,
            tornado_example.CheckRespHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        test_helper.json()

    def test_mock_route(self) -> None:
        assert (
            _TestHelper(
                self,
                tornado_example.MockHandler.get,
                path_dict={"age": 3},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
            ).json()
            == tornado_example.UserSuccessRespModel2.get_example_value()
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
        } == _TestHelper(
            self,
            tornado_example.PaitModelHanler.post,
            header_dict={"user-agent": "customer_agent"},
            query_dict={"uid": 123, "user_name": "appl"},
            body_dict={"user_info": {"age": 2, "user_name": "appl"}},
            strict_inspection_check_json_content=False,
        ).json()

    def test_depend(self) -> None:
        assert {"code": 0, "msg": "", "data": {"age": 2, "user_agent": "customer_agent"}} == _TestHelper(
            self,
            tornado_example.DependHandler.post,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json()

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_pre_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: _TestHelper = _TestHelper(
            self,
            tornado_example.PreDependContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_with("context_depend exit")
        test_helper = _TestHelper(
            self,
            tornado_example.PreDependContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_pre_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: _TestHelper = _TestHelper(
            self,
            tornado_example.PreDependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_with("context_depend exit")
        test_helper = _TestHelper(
            self,
            tornado_example.PreDependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: _TestHelper = _TestHelper(
            self,
            tornado_example.DependContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_with("context_depend exit")
        test_helper = _TestHelper(
            self,
            tornado_example.DependContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: _TestHelper = _TestHelper(
            self,
            tornado_example.DependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_with("context_depend exit")
        test_helper = _TestHelper(
            self,
            tornado_example.DependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_with("context_depend error")

    def test_get_cbv(self) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == _TestHelper(
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
        } == _TestHelper(
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

    def test_cache_response(self) -> None:
        def del_key(key: str) -> None:
            redis: Redis = Redis()
            for _key in redis.scan_iter(match=key + "*"):
                redis.delete(_key)

        # test not exc
        del_key("CacheResponse")
        result1: str = _TestHelper(self, tornado_example.CacheResponseHandler.get).text()
        result2: str = _TestHelper(self, tornado_example.CacheResponseHandler.get).text()
        result3: str = _TestHelper(self, tornado_example.CacheResponse1Handler.get).text()
        result4: str = _TestHelper(self, tornado_example.CacheResponse1Handler.get).text()
        assert result1 == result2
        assert result3 == result4
        assert result1 != result3
        assert result2 != result4
        del_key("CacheResponse")
        assert result1 != _TestHelper(self, tornado_example.CacheResponseHandler.get).text()
        assert result3 != _TestHelper(self, tornado_example.CacheResponse1Handler.get).text()

        # test not include exc
        # tornado exc handle exception
        del_key("CacheResponse")
        assert (
            _TestHelper(self, tornado_example.CacheResponseHandler.get, query_dict={"raise_exc": 1}).json()["code"]
            == -1
        )

        # test include exc
        del_key("CacheResponse")
        result_5 = _TestHelper(self, tornado_example.CacheResponseHandler.get, query_dict={"raise_exc": 2}).text()
        result_6 = _TestHelper(self, tornado_example.CacheResponseHandler.get, query_dict={"raise_exc": 2}).text()
        assert result_5 == result_6

    def test_cache_other_response_type(self) -> None:
        def _handler(_route_handler: Callable) -> Any:
            pait_core_model: "PaitCoreModel" = getattr(_route_handler, "pait_core_model")
            pait_response: Type[response.PaitBaseResponseModel] = pait_core_model.response_model_list[0]
            resp: HTTPResponse = _TestHelper(self, _route_handler).get()

            if issubclass(pait_response, response.PaitHtmlResponseModel) or issubclass(
                pait_response, response.PaitTextResponseModel
            ):
                return resp.body.decode()
            else:
                return resp.body

        key: str = "test_cache_other_response_type"

        async def del_cache() -> None:
            await tornado_example.Redis(decode_responses=True).delete(key)

        for route_handler in [tornado_example.TextResponseHanler.get, tornado_example.HtmlResponseHanler.get]:
            self.get_new_ioloop().run_sync(del_cache)
            with enable_plugin(route_handler, tornado_example.CacheResponsePlugin.build(name=key, cache_time=5)):
                tornado_example.CacheResponsePlugin.set_redis_to_app(
                    self.get_app(), tornado_example.Redis(decode_responses=True)
                )
                assert _handler(route_handler) == _handler(route_handler)

    def test_cache_response_param_name(self) -> None:
        key: str = "test_cache_response_param_name"

        async def del_cache() -> None:
            redis: tornado_example.Redis = tornado_example.Redis(decode_responses=True)
            async for _key in redis.scan_iter(match=key + "*"):
                await redis.delete(_key)

        self.get_new_ioloop().run_sync(del_cache)
        route_handler: Callable = tornado_example.PostHandler.post

        with enable_plugin(
            route_handler,
            tornado_example.CacheResponsePlugin.build(name=key, enable_cache_name_merge_param=True, cache_time=5),
        ):
            tornado_example.CacheResponsePlugin.set_redis_to_app(
                self.get_app(), tornado_example.Redis(decode_responses=True)
            )
            test_helper1: _TestHelper = _TestHelper(
                self,
                route_handler,
                body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            )
            test_helper2: _TestHelper = _TestHelper(
                self,
                route_handler,
                body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "woman"},
            )
            assert test_helper1.json() == test_helper1.json()
            assert test_helper2.json() == test_helper2.json()
            assert test_helper1.json() != test_helper2.json()

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
        import os

        from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
        from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc
        from pait.app.tornado import load_app
        from pait.app.tornado.grpc_route import GrpcGatewayRoute
        from pait.util.grpc_inspect.message_to_pydantic import grpc_timestamp_int_handler

        project_path: str = os.getcwd().split("pait/")[0]
        if project_path.endswith("pait"):
            project_path += "/"
        elif not project_path.endswith("pait/"):
            project_path = os.path.join(project_path, "pait/")
        grpc_path: str = project_path + "example/example_grpc/"

        prefix: str = "/api-test"
        GrpcGatewayRoute(
            self._app,
            user_pb2_grpc.UserStub,
            social_pb2_grpc.BookSocialStub,
            manager_pb2_grpc.BookManagerStub,
            prefix=prefix + "/",
            title="Grpc-test",
            grpc_timestamp_handler_tuple=(int, grpc_timestamp_int_handler),
            parse_msg_desc=grpc_path,
        )
        grpc_test_openapi(load_app(self._app), url_prefix=prefix)
