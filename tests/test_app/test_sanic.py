import json
import sys
from tempfile import NamedTemporaryFile
from typing import Callable, Generator, Type
from unittest import mock

import pytest
from pytest_mock import MockFixture
from sanic import Sanic
from sanic_testing import TestManager as SanicTestManager  # type: ignore
from sanic_testing.testing import SanicTestClient
from sanic_testing.testing import TestingResponse as Response  # type: ignore

from example.param_verify import sanic_example
from pait.app import auto_load_app
from pait.app.sanic import SanicTestHelper
from pait.model import response
from tests.conftest import enable_mock


@pytest.fixture
def client() -> Generator[SanicTestClient, None, None]:
    app: Sanic = sanic_example.create_app()
    SanicTestManager(app)
    yield app.test_client


def response_test_helper(
    client: SanicTestClient, route_handler: Callable, pait_response: Type[response.PaitBaseResponseModel]
) -> None:
    from pait.app.sanic.plugin.mock_response import MockPlugin

    test_helper: SanicTestHelper = SanicTestHelper(client, route_handler)
    test_helper.get()

    with enable_mock(route_handler, MockPlugin):
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
        msg: str = SanicTestHelper(client, sanic_example.raise_tip_route, header_dict={"Content-Type": "test"}).json()[
            "msg"
        ]
        assert 'File "/home/so1n/github/pait/example/param_verify/sanic_example.py", ' in msg
        assert "in raise_tip_route. error:content__type value is <class 'pydantic.fields.UndefinedType'>" in msg

    def test_post(self, client: SanicTestClient) -> None:
        test_helper: SanicTestHelper = SanicTestHelper(
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
            assert client.get(url)[1].json["code"] == api_code

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
        assert {"code": 0, "msg": "", "data": {"age": 2, "user_agent": "customer_agent"}} == SanicTestHelper(
            client,
            sanic_example.depend_route,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json()

    def test_same_alias_name(self, client: SanicTestClient) -> None:
        assert (
            SanicTestHelper(
                client,
                sanic_example.same_alias_route,
                query_dict={"token": "query"},
                header_dict={"token": "header"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        )
        assert (
            SanicTestHelper(
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
            SanicTestHelper(
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
            } == SanicTestHelper(
                client,
                sanic_example.pait_base_field_route,
                file_dict={"upload_file": f1},
                form_dict={"a": "1", "b": "2", "c": ["3", "4"]},
                cookie_dict={"cookie": "abcd=abcd;"},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                path_dict={"age": 2},
                strict_inspection_check_json_content=False,
            ).json()

    def test_check_param(self, client: SanicTestClient) -> None:
        test_helper: SanicTestHelper = SanicTestHelper(
            client,
            sanic_example.check_param_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
        )
        assert "requires at most one of param user_name or alias_user_name" in test_helper.json()["msg"]
        test_helper = SanicTestHelper(
            client,
            sanic_example.check_param_route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01"},
        )
        assert "birthday requires param alias_user_name, which if not none" in test_helper.json()["msg"]

    def test_check_response(self, client: SanicTestClient) -> None:
        test_helper: SanicTestHelper = SanicTestHelper(
            client,
            sanic_example.check_response_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            test_helper.json()
        test_helper = SanicTestHelper(
            client,
            sanic_example.check_response_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        test_helper.json()

    def test_mock_route(self, client: SanicTestClient) -> None:
        assert (
            SanicTestHelper(
                client,
                sanic_example.mock_route,
                path_dict={"age": 3},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
            ).json()
            == json.loads(sanic_example.UserSuccessRespModel2.get_example_value())
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
        } == SanicTestHelper(
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
        test_helper: SanicTestHelper = SanicTestHelper(
            client,
            sanic_example.depend_contextmanager_route,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = SanicTestHelper(
            client,
            sanic_example.depend_contextmanager_route,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_pre_depend_contextmanager(self, client: SanicTestClient, mocker: MockFixture) -> None:
        error_logger = mocker.patch("example.param_verify.model.logging.error")
        info_logger = mocker.patch("example.param_verify.model.logging.info")
        test_helper: SanicTestHelper = SanicTestHelper(
            client,
            sanic_example.pre_depend_contextmanager_route,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = SanicTestHelper(
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
        } == SanicTestHelper(
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
        } == SanicTestHelper(
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
            SanicTestHelper(client, sanic_example.text_response_route).request()
        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import sanic

        with mock.patch.dict("sys.modules", sys.modules):
            assert sanic == auto_load_app.auto_load_app_class()
