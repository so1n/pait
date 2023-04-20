import datetime
import traceback
from typing import Callable, Generator, List, Type

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from redis import Redis  # type: ignore

from example.flask_example import main_example
from pait import field
from pait.app.base.app_helper import BaseAppHelper
from pait.model import PaitCoreModel, response
from pait.param_handle import ParamHandler
from pait.plugin import PluginManager
from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.plugin.base import PostPluginProtocol, PrePluginProtocol
from pait.plugin.cache_response import CacheResponsePlugin
from pait.plugin.check_json_resp import CheckJsonRespPlugin
from pait.plugin.mock_response import MockPluginProtocol


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    app: Flask = main_example.create_app()
    client: FlaskClient = app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


class TestPlugin:
    def test_add_plugin(self) -> None:
        class NotPrePlugin(PostPluginProtocol):
            pass

        class PrePlugin(PrePluginProtocol):
            pass

        def demo() -> None:
            pass

        core_model: PaitCoreModel = PaitCoreModel(
            demo,
            BaseAppHelper,
        )

        raw_plugin_list: List[PluginManager] = core_model._plugin_list
        raw_post_plugin_list: List[PluginManager] = core_model._post_plugin_list

        try:
            core_model.add_plugin([PluginManager(NotPrePlugin)], [PluginManager(NotPrePlugin)])  # type: ignore
        except Exception:
            assert "is post plugin" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

        try:
            core_model.add_plugin([PluginManager(PrePlugin)], [PluginManager(PrePlugin)])  # type: ignore
        except Exception:
            assert "is pre plugin" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

        assert core_model._plugin_list == raw_plugin_list
        assert core_model._post_plugin_list == raw_post_plugin_list


class TestJsonPlugin:
    def test_param(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            CheckJsonRespPlugin.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                ),
                {"check_resp_fn": ""},
            )

        exec_msg: str = e.value.args[0]
        assert "Please use response_model_list param" in exec_msg

    def test_response_model_is_not_json_resp(self) -> None:
        class DemoCoreTestResponseModel(response.TextResponseModel):
            is_core = True

        def demo() -> None:
            pass

        with pytest.raises(ValueError) as e:
            CheckJsonRespPlugin.pre_load_hook(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[DemoCoreTestResponseModel]), {}
            )

        exec_msg: str = e.value.args[0]
        assert "pait_response_model must " in exec_msg


class TestAutoCompleteJsonPlugin:
    def test_param(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            AutoCompleteJsonRespPlugin.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                ),
                {"default_response_dict": ""},
            )

        exec_msg: str = e.value.args[0]
        assert "Please use response_model_list param" in exec_msg

    def test_response_model_is_not_json_resp(self) -> None:
        class DemoCoreTestResponseModel(response.TextResponseModel):
            is_core = True

        def demo() -> None:
            pass

        with pytest.raises(ValueError) as e:
            AutoCompleteJsonRespPlugin.pre_load_hook(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[DemoCoreTestResponseModel]), {}
            )

        exec_msg: str = e.value.args[0]
        assert "pait_response_model must " in exec_msg

    def test_resp_not_sub_data(self) -> None:
        from example.common.response_model import AutoCompleteRespModel

        class FakePluginCoreModel:
            func: Callable = lambda: None

        plugin = AutoCompleteJsonRespPlugin(
            lambda *args, **kwargs: None,
            FakePluginCoreModel(),  # type: ignore
            default_response_dict=AutoCompleteRespModel.get_default_dict(),
        )
        assert plugin.merge({"code": 0}) == {
            "code": 0,
            "msg": "success",
            "data": {"uid": 100, "music_list": [{"name": "", "url": "", "singer": ""}], "image_list": [{}]},
        }


class TestMockPlugin:
    def test_not_found_response_model(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            MockPluginProtocol.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                ),
                {},
            )

        exec_msg: str = e.value.args[0]
        assert "can not found response model" in exec_msg

    def test_param(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            MockPluginProtocol.pre_check_hook(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[response.JsonResponseModel]),
                {"pait_response_model": ""},
            )

        exec_msg: str = e.value.args[0]
        assert "Please use response_model_list param" in exec_msg

    def test_fileter_fn(self) -> None:
        def demo() -> None:
            pass

        def filter_response(pait_response: Type[response.BaseResponseModel]) -> bool:
            if issubclass(pait_response, response.TextResponseModel):
                return True
            else:
                return False

        kwargs: dict = MockPluginProtocol.pre_load_hook(
            PaitCoreModel(
                demo,
                BaseAppHelper,
                response_model_list=[response.JsonResponseModel, response.TextResponseModel],
            ),
            {"enable_mock_response_filter_fn": filter_response},
        )
        assert kwargs["pait_response_model"] == response.TextResponseModel

    def test_get_pait_response_model(self) -> None:
        def demo() -> None:
            pass

        kwargs: dict = MockPluginProtocol.pre_load_hook(
            PaitCoreModel(
                demo,
                BaseAppHelper,
                response_model_list=[response.JsonResponseModel, response.TextResponseModel],
            ),
            {},
        )
        assert kwargs["pait_response_model"] == response.JsonResponseModel


class TestParamPlugin:
    def test_error_default_value(self) -> None:
        def demo(value: str = field.Query.i(default=datetime.datetime.now())) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "default type must <class 'str'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

    def test_error_default_factory_value(self) -> None:
        def demo(value: str = field.Query.i(default_factory=datetime.datetime.now)) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "default_factory type must <class 'str'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

    def test_error_example_value(self) -> None:
        def demo(value: str = field.Query.i(example=datetime.datetime.now())) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "example type must <class 'str'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

        def demo1(value: str = field.Query.i(example=datetime.datetime.now())) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo1,
                    BaseAppHelper,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "example type must <class 'str'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")


class TestCacheResponsePlugin:
    def test_not_set_response_model(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            CacheResponsePlugin.build(redis=Redis()).pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                ),
            )

        exec_msg = e.value.args[0]
        assert "can not found response model" in exec_msg

    def test_set_error_response_model(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            CacheResponsePlugin.build(redis=Redis()).pre_check_hook(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[response.FileResponseModel]),
            )

        exec_msg = e.value.args[0]
        assert f"Not use {CacheResponsePlugin.__name__} in " in exec_msg

    def test_set_error_redis(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(ValueError) as e:
            CacheResponsePlugin.build(redis=Redis(decode_responses=False)).pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
            )
        exec_msg = e.value.args[0]
        assert "Please set redis`s param:decode_responses to True" in exec_msg
