from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import Any, List, Mapping, Optional, Type, Union

import pytest
from pydantic import BaseModel, Field

from pait import field
from pait.app.base.adapter.request import BaseRequest
from pait.app.base.app_helper import BaseAppHelper
from pait.app.base.security.api_key import BaseAPIKey
from pait.app.base.security.base import BaseSecurity
from pait.app.base.security.http import BaseHTTPBasic
from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.base.test_helper import BaseTestHelper, CheckResponseBodyException, CheckResponseException
from pait.model.core import PaitCoreModel
from pait.model.response import BaseResponseModel, FileResponseModel, HtmlResponseModel, JsonResponseModel
from pait.param_handle import ParamHandler


class TestBaseAppHelper:
    def test_init(self) -> None:
        class DemoRequest(object):
            pass

        class DemoPaitRequest(BaseRequest):
            RequestType = DemoRequest

        class MyAppHelper(BaseAppHelper):
            request_class = DemoPaitRequest

        request = DemoRequest()
        base_app_helper = MyAppHelper([request, 1, 2, 3], {"a": 1, "b": 2, "c": 3})
        assert isinstance(base_app_helper.request.request, DemoRequest)
        assert base_app_helper.request.args == [request, 1, 2, 3]
        assert base_app_helper.request.kwargs == {"a": 1, "b": 2, "c": 3}
        assert isinstance(base_app_helper.request.request_extend().request, DemoRequest)

        with pytest.raises(ValueError):
            MyAppHelper([1, 2, 3], {"a": 1, "b": 2, "c": 3})


class TestSecurity:
    def test_base_security(self) -> None:
        class Demo(object):
            def __call__(self, *args: Any, **kwargs: Any) -> None:
                pass

            def pait_handler(self) -> None:
                pass

        with pytest.raises(ValueError) as e:
            BaseSecurity().set_pait_handler(Demo())

        exec_msg: str = e.value.args[0]
        assert "'func' already has pait_handler" == exec_msg

        def demo() -> None:
            pass

        with pytest.raises(ValueError) as e:
            BaseSecurity().set_pait_handler(demo)

        exec_msg = e.value.args[0]
        assert "has no __call__" in exec_msg

        class MySecurity(BaseSecurity):
            def __call__(self, a: int, b: int) -> int:
                return 0

        def error_demo_1(a: str) -> int:
            return 0

        with pytest.raises(ValueError) as e:
            MySecurity().set_pait_handler(error_demo_1)
        exec_msg = e.value.args[0]
        assert "func parameter a annotation not match" == exec_msg

        def error_demo_2(a: int, b: int) -> str:
            return ""

        with pytest.raises(ValueError) as e:
            MySecurity().set_pait_handler(error_demo_2)
        exec_msg = e.value.args[0]
        assert "func return annotation not match" == exec_msg

        def error_demo_3(a: int) -> int:
            return 0

        with pytest.raises(ValueError) as e:
            MySecurity().set_pait_handler(error_demo_3)
        exec_msg = e.value.args[0]
        assert "func parameter length not equal" == exec_msg

        def normal_demo(a: int, b: int) -> int:
            return 0

        MySecurity().set_pait_handler(normal_demo)

    def test_base_apikey(self) -> None:
        with pytest.raises(ValueError):
            BaseAPIKey(name="demo", field=field.Body.i())

        base_api_key = BaseAPIKey(name="demo", field=field.Query.i())
        assert base_api_key.pait_handler("aaa") == "aaa"
        assert base_api_key.authorization_handler("aaa") == "aaa"

        base_api_key = BaseAPIKey(name="demo", field=field.Query.i(), verify_api_key_callable=lambda x: "demo" in x)
        base_api_key.authorization_handler("demo aaa")
        with pytest.raises(NotImplementedError):
            base_api_key.authorization_handler("a")

    def test_base_http_basic(self) -> None:
        from any_api.openapi.model.openapi.security import HttpSecurityModel

        with pytest.raises(ValueError):
            BaseHTTPBasic(security_model=HttpSecurityModel(scheme="demo"))

        # authorization_handler test in test_xxx(app)


class TestSimpleRoute:
    def test_simple_route(self) -> None:
        from pait.plugin.unified_response import UnifiedResponsePlugin

        with pytest.raises(RuntimeError):
            add_route_plugin(
                SimpleRoute(
                    methods=["get"],
                    route=lambda x: x,
                    url="/api/demo",
                ),
                UnifiedResponsePlugin,
            )


@dataclass
class DemoResp(object):
    status_code: int = dc_field(default=200)
    headers: Mapping = dc_field(default_factory=lambda: {"x-demo": "gululu"})
    content_type: str = dc_field(default="application/json")
    text: str = dc_field(default="demo")
    get_bytes: bytes = dc_field(default=b"demo")
    json: Any = dc_field(default=None)


class TestBaseTestHelper:
    def test_func_not_found_pait_id(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError):
            BaseTestHelper(object(), demo)

    def _get_test_helper(self, response_model_list: Optional[List[Type[BaseResponseModel]]] = None) -> BaseTestHelper:
        class MyTestHelper(BaseTestHelper[DemoResp]):
            def _replace_path(self, path_str: str) -> Optional[str]:
                return path_str

            def _app_init_field(self) -> None:
                pass

            @staticmethod
            def _get_status_code(resp: DemoResp) -> int:
                return resp.status_code

            @staticmethod
            def _get_content_type(resp: DemoResp) -> str:
                return resp.content_type

            @staticmethod
            def _get_headers(resp: DemoResp) -> Mapping:
                return resp.headers

            @staticmethod
            def _get_text(resp: DemoResp) -> str:
                return resp.text

            @staticmethod
            def _get_bytes(resp: DemoResp) -> bytes:
                return resp.get_bytes

            @staticmethod
            def _get_json(resp: DemoResp) -> dict:
                return resp.json

        def demo() -> None:
            pass

        demo_core_model = PaitCoreModel(
            func=demo,
            app_helper_class=BaseAppHelper,
            param_handler_plugin=ParamHandler,
            response_model_list=response_model_list,
        )
        pait_dict = {demo_core_model.pait_id: demo_core_model}

        return MyTestHelper(object, demo, pait_dict=pait_dict)

    def test_custom_pait_dict(self) -> None:
        def demo() -> None:
            pass

        class MyTestHelper(BaseTestHelper[DemoResp]):
            def _replace_path(self, path_str: str) -> Optional[str]:
                return path_str

            def _app_init_field(self) -> None:
                pass

        demo_core_model = PaitCoreModel(func=demo, app_helper_class=BaseAppHelper, param_handler_plugin=ParamHandler)
        pait_dict = {demo_core_model.pait_id: demo_core_model}
        base_test_helper = MyTestHelper(object, demo, pait_dict=pait_dict)
        assert base_test_helper.pait_dict[demo_core_model.pait_id].func == demo

    def test_check_diff_resp(self) -> None:
        my_test_helper = self._get_test_helper()
        assert my_test_helper._check_diff_resp_dict(1, 1)
        assert my_test_helper._check_diff_resp_dict([1], [1])
        assert my_test_helper._check_diff_resp_dict([1], [1])
        assert my_test_helper._check_diff_resp_dict((1,), (1,))
        assert my_test_helper._check_diff_resp_dict({"a": 1}, {"a": 1})

        assert not my_test_helper._check_diff_resp_dict([1], ["1"])
        assert not my_test_helper._check_diff_resp_dict((1,), ("1",))
        assert not my_test_helper._check_diff_resp_dict({"a": 1}, {"a": "1"})

        with pytest.raises(CheckResponseBodyException) as e:
            assert my_test_helper._check_diff_resp_dict({"a": 1, "b": 1}, {"a": 1})
        assert e.value.args[0] == "Can not found key from model, key:b"

        with pytest.raises(CheckResponseBodyException) as e:
            assert my_test_helper._check_diff_resp_dict(
                {"a": 1, "b": [{"c": {"d": 1}}]},
                {"a": 1, "b": [{"c": "d"}]},
            )
        assert e.value.args[0] == "Can not found key from model, key:b -> c -> d"

    def test_assert_response(self) -> None:
        assert not self._get_test_helper()._assert_response(object)

        class HeaderModel(BaseModel):
            header_1: str = Field()
            header_2: int = Field()

        class HtmlErrorRespModel(HtmlResponseModel):
            status_code = (400,)
            header = HeaderModel

        result = self._get_test_helper(response_model_list=[HtmlErrorRespModel])._assert_response(DemoResp())
        assert isinstance(result, CheckResponseException) and result.message
        assert "check text content type error" not in result.message
        assert (
            "Get the response with a status code of 200, but the response_model specifies a status of (400,)"
            in result.message
        )
        assert (
            "Get the response with a media type of application/json,"
            " but the response_model specifies a media type of text/html"
        ) in result.message
        assert "Can not found header:header_1 in {'x-demo': 'gululu'}" in result.message
        assert "Can not found header:header_2 in {'x-demo': 'gululu'}" in result.message

        result = self._get_test_helper(response_model_list=[HtmlErrorRespModel])._assert_response(
            DemoResp(text=1)  # type: ignore
        )
        assert isinstance(result, CheckResponseException) and result.message
        assert "check text content type error" in result.message

        result = self._get_test_helper(response_model_list=[FileResponseModel])._assert_response(
            DemoResp(get_bytes=b"1")
        )
        assert isinstance(result, CheckResponseException) and result.message
        assert "check bytes content type error" not in result.message
        result = self._get_test_helper(response_model_list=[FileResponseModel])._assert_response(
            DemoResp(get_bytes="1")  # type: ignore
        )
        assert isinstance(result, CheckResponseException) and result.message
        assert "check bytes content type error" in result.message

        result = self._get_test_helper(response_model_list=[BaseResponseModel])._assert_response(DemoResp())
        assert isinstance(result, TypeError)
        assert "Pait not support response model" in result.args[0]

    def test_assert_json_response(self) -> None:
        class NotDataJsonRespModel(JsonResponseModel):
            response_data = None

        class SubDemoModel(BaseModel):
            a: List[str] = Field(example=["1"])  # type:ignore[call-arg]

        class BaseDemoModel(BaseModel):
            a: int = Field(example=1)  # type:ignore[call-arg]
            c: SubDemoModel

        class DemoModel(BaseDemoModel):
            b: str = Field()

        class OtherDemoModel(BaseDemoModel):
            e: int = Field(default=1)
            # Use example column to force the value of the check to be set`"1"`
            f: Union[int, str] = Field(example="1")  # type:ignore[call-arg]

        class JsonRespModel(JsonResponseModel):
            response_data: Type[BaseModel] = DemoModel

        class OtherJsonRespModel(JsonRespModel):
            response_data: Type[BaseModel] = OtherDemoModel

        assert self._get_test_helper(response_model_list=[NotDataJsonRespModel])._assert_response(DemoResp()) is None

        result = self._get_test_helper(response_model_list=[JsonRespModel])._assert_response(DemoResp())
        assert isinstance(result, CheckResponseException) and result.message
        assert "response error result" in result.message

        assert (
            self._get_test_helper(response_model_list=[JsonRespModel])._assert_response(
                DemoResp(json={"a": 1, "b": "a", "c": {"a": ["a"]}})
            )
            is None
        )

        result = self._get_test_helper(response_model_list=[JsonRespModel])._assert_response(
            DemoResp(json={"a": 1, "b": "a", "c": {"a": "1"}})
        )
        assert isinstance(result, CheckResponseException) and result.message
        assert "check json content error" in result.message

        result = self._get_test_helper(response_model_list=[JsonRespModel])._assert_response(
            DemoResp(json={"a": 1, "b": "a", "c": {"a": ["1"]}, "d": 1})
        )
        assert isinstance(result, CheckResponseException) and result.message
        assert "check json content error, exec" in result.message

        result = self._get_test_helper(response_model_list=[OtherJsonRespModel])._assert_response(
            DemoResp(json={"a": 1, "c": {"a": ["1"]}, "f": 1})
        )
        assert isinstance(result, CheckResponseException) and result.message
        assert "check json structure error" in result.message
