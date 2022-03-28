import datetime
from typing import Generator, List, Type

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient

from example.param_verify import flask_example
from pait import field
from pait.app.base.app_helper import BaseAppHelper
from pait.exceptions import TipException
from pait.model import response
from pait.model.core import PaitCoreModel
from pait.param_handle import ParamHandler
from pait.plugin import PluginManager
from pait.plugin.at_most_one_of import AsyncAtMostOneOfPlugin, AtMostOneOfPlugin
from pait.plugin.auto_complete_json_resp import AsyncAutoCompleteJsonRespPlugin, AutoCompleteJsonRespPlugin
from pait.plugin.base import BasePlugin
from pait.plugin.base_mock_response import BaseAsyncMockPlugin, BaseMockPlugin
from pait.plugin.check_json_resp import AsyncCheckJsonRespPlugin, CheckJsonRespPlugin
from pait.plugin.required import AsyncRequiredPlugin, RequiredPlugin


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    app: Flask = flask_example.create_app()
    client: FlaskClient = app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


class TestPlugin:
    def test_add_plugin(self) -> None:
        class NotPrePlugin(BasePlugin):
            is_pre_core = False

        class PrePlugin(BasePlugin):
            is_pre_core = True

        def demo() -> None:
            pass

        core_model: PaitCoreModel = PaitCoreModel(
            demo,
            BaseAppHelper,
        )

        raw_plugin_list: List[PluginManager] = core_model._plugin_list
        raw_post_plugin_list: List[PluginManager] = core_model._post_plugin_list

        with pytest.raises(ValueError) as e:
            core_model.add_plugin([PluginManager(NotPrePlugin)], [PluginManager(NotPrePlugin)])
        exec_msg: str = e.value.args[0]
        assert "is post plugin" in exec_msg

        with pytest.raises(ValueError) as e:
            core_model.add_plugin([PluginManager(PrePlugin)], [PluginManager(PrePlugin)])
        exec_msg = e.value.args[0]
        assert "is pre plugin" in exec_msg
        assert core_model._plugin_list == raw_plugin_list
        assert core_model._post_plugin_list == raw_post_plugin_list

    def test_async_plugin_in_sync_func(self) -> None:
        def demo() -> None:
            pass

        for test_plugin in [
            AsyncAtMostOneOfPlugin,
            AsyncAutoCompleteJsonRespPlugin,
            BaseAsyncMockPlugin,
            AsyncRequiredPlugin,
            AsyncCheckJsonRespPlugin,
        ]:
            with pytest.raises(TypeError) as e:
                test_plugin.cls_hook_by_core_model(  # type: ignore
                    PaitCoreModel(
                        demo,
                        BaseAppHelper,
                    ),
                    {},
                )

            exec_msg: str = e.value.args[0]
            assert "Plugin only support async func" in exec_msg

    def test_sync_plugin_in_async_func(self) -> None:
        async def demo() -> None:
            pass

        for plugin in [
            AtMostOneOfPlugin,
            AutoCompleteJsonRespPlugin,
            BaseMockPlugin,
            RequiredPlugin,
            CheckJsonRespPlugin,
        ]:
            with pytest.raises(TypeError) as e:
                plugin.cls_hook_by_core_model(  # type: ignore
                    PaitCoreModel(
                        demo,
                        BaseAppHelper,
                    ),
                    {},
                )

            exec_msg: str = e.value.args[0]
            assert "Plugin not support async func" in exec_msg


class TestJsonPlugin:
    def test_param(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            CheckJsonRespPlugin.cls_hook_by_core_model(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                ),
                {"check_resp_fn": ""},
            )

        exec_msg: str = e.value.args[0]
        assert "Please use response_model_list param" in exec_msg

    def test_response_model_is_not_json_resp(self) -> None:
        class DemoCoreTestResponseModel(response.PaitTextResponseModel):
            is_core = True

        def demo() -> None:
            pass

        with pytest.raises(ValueError) as e:
            CheckJsonRespPlugin.cls_hook_by_core_model(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[DemoCoreTestResponseModel]), {}
            )

        exec_msg: str = e.value.args[0]
        assert "pait_response_model must " in exec_msg

    def test_fun_not_return_type(self) -> None:
        class DemoCoreJsonResponseModel(response.PaitJsonResponseModel):
            is_core = True

        def demo() -> None:
            pass

        with pytest.raises(ValueError) as e:
            CheckJsonRespPlugin.cls_hook_by_core_model(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[DemoCoreJsonResponseModel]), {}
            )

        exec_msg: str = e.value.args[0]
        assert "Can not found return type by func" in exec_msg

    def test_fun_return_type_is_not_dict_and_typed_dict(self) -> None:
        class DemoCoreJsonResponseModel(response.PaitJsonResponseModel):
            is_core = True

        def demo() -> int:
            pass

        with pytest.raises(ValueError) as e:
            CheckJsonRespPlugin.cls_hook_by_core_model(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[DemoCoreJsonResponseModel]), {}
            )

        exec_msg: str = e.value.args[0]
        assert "Can not found CheckJsonRespPlugin support return type" == exec_msg


class TestAutoCompleteJsonPlugin:
    def test_param(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            AutoCompleteJsonRespPlugin.cls_hook_by_core_model(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                ),
                {"pait_response_model": ""},
            )

        exec_msg: str = e.value.args[0]
        assert "Please use response_model_list param" in exec_msg

    def test_response_model_is_not_json_resp(self) -> None:
        class DemoCoreTestResponseModel(response.PaitTextResponseModel):
            is_core = True

        def demo() -> None:
            pass

        with pytest.raises(ValueError) as e:
            AutoCompleteJsonRespPlugin.cls_hook_by_core_model(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[DemoCoreTestResponseModel]), {}
            )

        exec_msg: str = e.value.args[0]
        assert "pait_response_model must " in exec_msg


class TestMockPlugin:
    def test_not_found_response_model(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            BaseMockPlugin.cls_hook_by_core_model(
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
            BaseMockPlugin.cls_hook_by_core_model(
                PaitCoreModel(demo, BaseAppHelper, response_model_list=[response.PaitJsonResponseModel]),
                {"pait_response_model": ""},
            )

        exec_msg: str = e.value.args[0]
        assert "Please use response_model_list param" in exec_msg

    def test_fileter_fn(self) -> None:
        def demo() -> None:
            pass

        def filter_response(pait_response: Type[response.PaitBaseResponseModel]) -> bool:
            if issubclass(pait_response, response.PaitTextResponseModel):
                return True
            else:
                return False

        kwargs: dict = BaseMockPlugin.cls_hook_by_core_model(
            PaitCoreModel(
                demo,
                BaseAppHelper,
                response_model_list=[response.PaitJsonResponseModel, response.PaitTextResponseModel],
            ),
            {"enable_mock_response_filter_fn": filter_response},
        )
        assert kwargs["pait_response_model"] == response.PaitTextResponseModel

    def test_get_pait_response_model(self) -> None:
        def demo() -> None:
            pass

        kwargs: dict = BaseMockPlugin.cls_hook_by_core_model(
            PaitCoreModel(
                demo,
                BaseAppHelper,
                response_model_list=[response.PaitJsonResponseModel, response.PaitTextResponseModel],
            ),
            {},
        )
        assert kwargs["pait_response_model"] == response.PaitJsonResponseModel


class TestParamPlugin:
    def test_error_default_value(self) -> None:
        def demo(value: str = field.Query(default=datetime.datetime.now())) -> None:
            pass

        with pytest.raises(TipException) as e:
            ParamHandler.cls_hook_by_core_model(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    response_model_list=[response.PaitJsonResponseModel, response.PaitTextResponseModel],
                ),
                {},
            )

        exec_msg: str = e.value.args[0]
        assert "default type must <class 'str'>" in exec_msg

    def test_error_default_factory_value(self) -> None:
        def demo(value: str = field.Query(default_factory=datetime.datetime.now)) -> None:
            pass

        with pytest.raises(TipException) as e:
            ParamHandler.cls_hook_by_core_model(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    response_model_list=[response.PaitJsonResponseModel, response.PaitTextResponseModel],
                ),
                {},
            )

        exec_msg: str = e.value.args[0]
        assert "default_factory type must <class 'str'>" in exec_msg

    def test_error_example_value(self) -> None:
        def demo(value: str = field.Query(example=datetime.datetime.now())) -> None:
            pass

        with pytest.raises(TipException) as e:
            ParamHandler.cls_hook_by_core_model(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    response_model_list=[response.PaitJsonResponseModel, response.PaitTextResponseModel],
                ),
                {},
            )

        exec_msg: str = e.value.args[0]
        assert "example type must <class 'str'>" in exec_msg

        def demo1(value: str = field.Query(example=datetime.datetime.now())) -> None:
            pass

        with pytest.raises(TipException) as e:
            ParamHandler.cls_hook_by_core_model(
                PaitCoreModel(
                    demo1,
                    BaseAppHelper,
                    response_model_list=[response.PaitJsonResponseModel, response.PaitTextResponseModel],
                ),
                {},
            )

        exec_msg = e.value.args[0]
        assert "example type must <class 'str'>" in exec_msg
