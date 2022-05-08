import difflib
import json
import sys
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Callable, Generator, Type
from unittest import mock

import pytest
from pytest_mock import MockFixture
from redis import Redis  # type: ignore
from sanic import Sanic
from sanic_testing import TestManager as SanicTestManager  # type: ignore
from sanic_testing.testing import SanicTestClient
from sanic_testing.testing import TestingResponse as Response  # type: ignore

from example.param_verify import sanic_example
from pait.api_doc.html import get_redoc_html, get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenAPI
from pait.app import auto_load_app
from pait.app.sanic import TestHelper as _TestHelper
from pait.app.sanic import load_app
from pait.model import response
from tests.conftest import enable_plugin

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


@pytest.fixture
def client() -> Generator[SanicTestClient, None, None]:
    app: Sanic = sanic_example.create_app()
    SanicTestManager(app)
    yield app.test_client


def response_test_helper(
    client: SanicTestClient, route_handler: Callable, pait_response: Type[response.PaitBaseResponseModel]
) -> None:
    from pait.app.sanic.plugin.mock_response import AsyncMockPlugin

    test_helper: _TestHelper = _TestHelper(client, route_handler)
    test_helper.get()

    with enable_plugin(route_handler, AsyncMockPlugin.build()):
        resp: Response = test_helper.get()
        for key, value in pait_response.header.items():
            assert resp.headers[key] == value
        if issubclass(pait_response, response.PaitHtmlResponseModel) or issubclass(
            pait_response, response.PaitTextResponseModel
        ):
            assert resp.text == pait_response.get_example_value()
        else:
            assert resp.content == pait_response.get_example_value()


class TestSanic:
    def test_raise_tip_route(self, client: SanicTestClient) -> None:
        msg: str = _TestHelper(client, sanic_example.raise_tip_route, header_dict={"Content-Type": "test"}).json()[
            "msg"
        ]
        assert msg == "error param:content__type, Can not found content__type value"

    def test_post(self, client: SanicTestClient) -> None:
        test_helper: _TestHelper = _TestHelper(
            client,
            sanic_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            test_helper.json(),
            client.post(
                "/api/post",
                headers={"user-agent": "customer_agent"},
                json={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            )[1].json,
        ]:
            assert resp["code"] == 0
            assert resp["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/json",
                "sex": "man",
            }

    def test_check_json_route(self, client: SanicTestClient) -> None:
        for url, api_code in [
            (
                "/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10", -1),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = client.get(url)[1].json
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_auto_complete_json_route(self, client: SanicTestClient) -> None:
        def check_dict(source_dict: dict, target_dict: dict) -> None:
            for key, value in source_dict.items():
                if isinstance(value, dict) and key in target_dict:
                    return check_dict(value, target_dict[key])
                else:
                    if key not in target_dict or not isinstance(value, type(target_dict[key])):
                        raise RuntimeError("check error")

        auto_complete_dict: dict = client.get("/api/auto-complete-json-plugin?uid=123&user_name=appl&sex=man&age=10")[
            1
        ].json
        real_dict: dict = client.get(
            "/api/auto-complete-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1"
        )[1].json
        check_dict(auto_complete_dict, real_dict)

    def test_depend_route(self, client: SanicTestClient) -> None:
        assert {"code": 0, "msg": "", "data": {"age": 2, "user_agent": "customer_agent"}} == _TestHelper(
            client,
            sanic_example.depend_route,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json()

    def test_same_alias_name(self, client: SanicTestClient) -> None:
        assert (
            _TestHelper(
                client,
                sanic_example.same_alias_route,
                query_dict={"token": "query"},
                header_dict={"token": "header"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        )
        assert (
            _TestHelper(
                client,
                sanic_example.same_alias_route,
                query_dict={"token": "query1"},
                header_dict={"token": "header1"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query1", "header_token": "header1"}}
        )

    def test_field_default_factory_route(self, client: SanicTestClient) -> None:
        assert (
            _TestHelper(
                client,
                sanic_example.field_default_factory_route,
                body_dict={"demo_value": 0},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"demo_value": 0, "data_list": [], "data_dict": {}}}
        )

    def test_pait_base_field_route(self, client: SanicTestClient) -> None:
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
                    "filename": f1.name.split("/")[-1],
                    "form_a": "1",
                    "form_b": "2",
                    "form_c": ["3", "4"],
                    "multi_user_name": ["abc", "efg"],
                    "sex": "man",
                    "uid": 123,
                    "user_name": "appl",
                },
                "msg": "",
            } == _TestHelper(
                client,
                sanic_example.pait_base_field_route,
                file_dict={"upload_file": f1},
                form_dict={"a": "1", "b": "2", "c": ["3", "4"]},
                cookie_dict={"abcd": "abcd"},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                path_dict={"age": 2},
                strict_inspection_check_json_content=False,
            ).json()

    def test_check_param(self, client: SanicTestClient) -> None:
        test_helper: _TestHelper = _TestHelper(
            client,
            sanic_example.check_param_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert "requires at most one of param user_name or alias_user_name" in test_helper.json()["msg"]
        test_helper = _TestHelper(
            client,
            sanic_example.check_param_route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01"},
            strict_inspection_check_json_content=False,
        )
        assert "birthday requires param alias_user_name, which if not none" in test_helper.json()["msg"]
        test_helper = _TestHelper(
            client,
            sanic_example.check_param_route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01", "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert test_helper.json()["code"] == 0

    def test_check_response(self, client: SanicTestClient) -> None:
        test_helper: _TestHelper = _TestHelper(
            client,
            sanic_example.check_response_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            test_helper.json()
        test_helper = _TestHelper(
            client,
            sanic_example.check_response_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        test_helper.json()

    def test_mock_route(self, client: SanicTestClient) -> None:
        assert (
            _TestHelper(
                client,
                sanic_example.mock_route,
                path_dict={"age": 3},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
            ).json()
            == sanic_example.UserSuccessRespModel2.get_example_value()
        )

    def test_pait_model(self, client: SanicTestClient) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {
                "uid": 123,
                "user_agent": "customer_agent",
                "user_info": {"age": 2, "user_name": "appl"},
            },
        } == _TestHelper(
            client,
            sanic_example.pait_model_route,
            header_dict={"user-agent": "customer_agent"},
            query_dict={"uid": 123, "user_name": "appl"},
            body_dict={"user_info": {"age": 2, "user_name": "appl"}},
            strict_inspection_check_json_content=False,
        ).json()

    def test_depend_contextmanager(self, client: SanicTestClient, mocker: MockFixture) -> None:
        error_logger = mocker.patch("example.param_verify.model.logging.error")
        info_logger = mocker.patch("example.param_verify.model.logging.info")
        test_helper: _TestHelper = _TestHelper(
            client,
            sanic_example.depend_contextmanager_route,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = _TestHelper(
            client,
            sanic_example.depend_contextmanager_route,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_pre_depend_contextmanager(self, client: SanicTestClient, mocker: MockFixture) -> None:
        error_logger = mocker.patch("example.param_verify.model.logging.error")
        info_logger = mocker.patch("example.param_verify.model.logging.info")
        test_helper: _TestHelper = _TestHelper(
            client,
            sanic_example.pre_depend_contextmanager_route,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = _TestHelper(
            client,
            sanic_example.pre_depend_contextmanager_route,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_get_cbv(self, client: SanicTestClient) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == _TestHelper(
            client,
            sanic_example.CbvRoute.get,
            query_dict={"uid": "123", "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"Content-Type": "application/json"},
        ).json()

    def test_post_cbv(self, client: SanicTestClient) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == _TestHelper(
            client,
            sanic_example.CbvRoute.post,
            body_dict={"uid": "123", "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"Content-Type": "application/json"},
        ).json()

    def test_text_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, sanic_example.text_response_route, response.PaitTextResponseModel)

    def test_html_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, sanic_example.html_response_route, response.PaitHtmlResponseModel)

    def test_file_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, sanic_example.file_response_route, response.PaitFileResponseModel)

    def test_test_helper_not_support_mutil_method(self, client: SanicTestClient) -> None:
        client.app.add_route(sanic_example.text_response_route, "/api/new-text-resp", methods={"GET", "POST"})
        with pytest.raises(RuntimeError) as e:
            _TestHelper(client, sanic_example.text_response_route).request()
        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_doc_route(self, client: SanicTestClient) -> None:
        assert client.get("/swagger")[1].status_code == 404
        assert client.get("/redoc")[1].status_code == 404
        assert client.get("/swagger?pin_code=6666")[1].text == get_swagger_ui_html(
            f"http://{client.host}:{client.port}/openapi.json?pin_code=6666", "Pait Api Doc(private)"
        )
        assert client.get("/redoc?pin_code=6666")[1].text == get_redoc_html(
            f"http://{client.host}:{client.port}/openapi.json?pin_code=6666", "Pait Api Doc(private)"
        )
        assert (
            json.loads(client.get("/openapi.json?pin_code=6666&template-token=xxx")[1].text)["paths"]["/api/user"][
                "get"
            ]["parameters"][0]["schema"]["example"]
            == "xxx"
        )
        assert (
            difflib.SequenceMatcher(
                None,
                str(client.get("/openapi.json?pin_code=6666")[1].json),
                str(
                    PaitOpenAPI(
                        load_app(client.app),
                        title="Pait Doc",
                        open_api_server_list=[{"url": "http://localhost", "description": ""}],
                    ).open_api_dict
                ),
            ).quick_ratio()
            > 0.95
        )

    def test_cache_response(self, client: SanicTestClient) -> None:

        with pytest.raises(RuntimeError):
            # sanic will use a new event loop for each request,
            # and Reids initialization regrets giving the current event loop, so the second request will report an error
            _TestHelper(client, sanic_example.cache_response).text()
            _TestHelper(client, sanic_example.cache_response).text()

        for _ in range(3):
            Redis().delete("cache_response")
            Redis().delete("cache_response1")
            sanic_example.CacheResponsePlugin.set_redis_to_app(client.app, sanic_example.Redis(decode_responses=True))
            result1: str = _TestHelper(client, sanic_example.cache_response1).text()
            sanic_example.CacheResponsePlugin.set_redis_to_app(client.app, sanic_example.Redis(decode_responses=True))
            result2: str = _TestHelper(client, sanic_example.cache_response1).text()
            assert result1 == result2
            Redis().delete("cache_response")
            Redis().delete("cache_response1")
            sanic_example.CacheResponsePlugin.set_redis_to_app(client.app, sanic_example.Redis(decode_responses=True))
            assert result1 != _TestHelper(client, sanic_example.cache_response1).text()

    def test_cache_other_response_type(self, client: SanicTestClient) -> None:
        def _handler(_route_handler: Callable) -> Any:
            pait_core_model: "PaitCoreModel" = getattr(_route_handler, "pait_core_model")
            pait_response: Type[response.PaitBaseResponseModel] = pait_core_model.response_model_list[0]
            resp: Response = _TestHelper(client, _route_handler).get()
            if issubclass(pait_response, response.PaitHtmlResponseModel) or issubclass(
                pait_response, response.PaitTextResponseModel
            ):
                return resp.text
            else:
                return resp.content

        key: str = "test_cache_other_response_type"
        redis: Redis = Redis(decode_responses=True)

        for route_handler in [sanic_example.text_response_route, sanic_example.html_response_route]:
            redis.delete(key)
            with enable_plugin(route_handler, sanic_example.CacheResponsePlugin.build(name=key, cache_time=5)):
                sanic_example.CacheResponsePlugin.set_redis_to_app(
                    client.app, sanic_example.Redis(decode_responses=True)
                )
                result1: str = _handler(route_handler)
                sanic_example.CacheResponsePlugin.set_redis_to_app(
                    client.app, sanic_example.Redis(decode_responses=True)
                )
                result2: str = _handler(route_handler)
                assert result1 == result2

    def test_cache_response_param_name(self, client: SanicTestClient) -> None:
        key: str = "test_cache_response_param_name"
        redis: Redis = Redis(decode_responses=True)
        route_handler: Callable = sanic_example.post_route

        for _key in redis.scan_iter(match=key + "*"):
            redis.delete(_key)
        with enable_plugin(
            route_handler,
            sanic_example.CacheResponsePlugin.build(name=key, enable_cache_name_merge_param=True, cache_time=5),
        ):
            test_helper1: _TestHelper = _TestHelper(
                client,
                route_handler,
                body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            )
            test_helper2: _TestHelper = _TestHelper(
                client,
                route_handler,
                body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "woman"},
            )
            sanic_example.CacheResponsePlugin.set_redis_to_app(client.app, sanic_example.Redis(decode_responses=True))
            result1: dict = test_helper1.json()
            sanic_example.CacheResponsePlugin.set_redis_to_app(client.app, sanic_example.Redis(decode_responses=True))
            result2: dict = test_helper1.json()
            sanic_example.CacheResponsePlugin.set_redis_to_app(client.app, sanic_example.Redis(decode_responses=True))
            result3: dict = test_helper2.json()
            sanic_example.CacheResponsePlugin.set_redis_to_app(client.app, sanic_example.Redis(decode_responses=True))
            result4: dict = test_helper2.json()

            assert result1 == result2
            assert result3 == result4
            assert result1 != result3

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import sanic

        with mock.patch.dict("sys.modules", sys.modules):
            assert sanic == auto_load_app.auto_load_app_class()
