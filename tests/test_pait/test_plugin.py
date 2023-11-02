from typing import Callable, Generator

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from redis import Redis  # type: ignore

from example.flask_example import main_example
from pait import field
from pait.app.base.app_helper import BaseAppHelper
from pait.exceptions import CheckValueError
from pait.model import response
from pait.model.context import PluginContext
from pait.model.core import PaitCoreModel
from pait.model.response import FileResponseModel
from pait.param_handle import ParamHandler
from pait.plugin.at_most_one_of import AtMostOneOfExtraParam, AtMostOneOfPlugin
from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.plugin.check_json_resp import CheckJsonRespPlugin
from pait.plugin.mock_response import MockPluginProtocol
from pait.plugin.required import RequiredExtraParam, RequiredGroupExtraParam, RequiredPlugin
from pait.plugin.unified_response import UnifiedResponsePluginProtocol
from pait.util import get_pait_response_model


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


class TestAtMostOneOfPlugin:
    def test_pre_load_with_init_param(self) -> None:
        def demo1() -> None:
            pass

        demo_core_model_1 = PaitCoreModel(
            demo1,
            BaseAppHelper,
            ParamHandler,
        )

        with pytest.raises(ValueError):
            AtMostOneOfPlugin.pre_load_hook(demo_core_model_1, {"at_most_one_of_list": [["a", "b"]]})

        def demo2(
            a: int = field.Query.i(),
            b: int = field.Query.i(),
        ) -> None:
            pass

        demo_core_model_2 = PaitCoreModel(
            demo2,
            BaseAppHelper,
            ParamHandler,
        )
        AtMostOneOfPlugin.pre_load_hook(demo_core_model_2, {"at_most_one_of_list": [["a", "b"]]})

    def test_pre_load_with_extra_param(self) -> None:
        def demo(
            a: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="a")]),
            a1: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="a")]),
            b: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="b")]),
            b1: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="b")]),
        ) -> None:
            pass

        demo_core_model = PaitCoreModel(
            demo,
            BaseAppHelper,
            ParamHandler,
        )
        kwargs_dict: dict = {"at_most_one_of_list": []}
        AtMostOneOfPlugin.pre_load_hook(demo_core_model, kwargs=kwargs_dict)
        assert kwargs_dict == {"at_most_one_of_list": [["a", "a1"], ["b", "b1"]]}

    def test_check_param(self) -> None:
        def demo(
            a: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="a")]),
            a1: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="a")]),
            b: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="b")]),
            b1: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="b")]),
        ) -> None:
            pass

        class FakePluginCoreModel:
            func = demo

        plugin = AtMostOneOfPlugin(
            lambda *args, **kwargs: None,
            FakePluginCoreModel(),  # type: ignore
            at_most_one_of_list=[["a", "a1"], ["b", "b1"]],
        )
        plugin.check_param(
            PluginContext(
                cbv_instance=None,
                app_helper=BaseAppHelper,  # type: ignore
                pait_core_model=FakePluginCoreModel(),  # type: ignore
                args=[],
                kwargs={"a": 1, "b": 1},
            )
        )

        with pytest.raises(CheckValueError):
            plugin.check_param(
                PluginContext(
                    cbv_instance=None,
                    app_helper=BaseAppHelper,  # type: ignore
                    pait_core_model=FakePluginCoreModel(),  # type: ignore
                    args=[],
                    kwargs={"a": 1, "a1": 1},
                )
            )


class TestAutoCompleteJsonPlugin:
    def test_pre_check(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            AutoCompleteJsonRespPlugin.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    ParamHandler,
                ),
                {"default_response_dict": ""},
            )

        exec_msg: str = e.value.args[0]
        assert "Please use response_model_list param" in exec_msg

    def test_response_model_is_not_json_resp(self) -> None:
        class DemoCoreTestResponseModel(response.TextResponseModel):
            pass

        def demo() -> None:
            pass

        with pytest.raises(ValueError) as e:
            AutoCompleteJsonRespPlugin.pre_load_hook(
                PaitCoreModel(demo, BaseAppHelper, ParamHandler, response_model_list=[DemoCoreTestResponseModel]),
                {"get_pait_response_model": get_pait_response_model},
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


class TestCacheResponsePlugin:
    def test_not_set_response_model(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            CacheResponsePlugin.build(redis=Redis()).pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    ParamHandler,
                ),
            )

        exec_msg = e.value.args[0]
        assert "can not found response model" in exec_msg

    def test_set_error_response_model(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            CacheResponsePlugin.build(redis=Redis()).pre_check_hook(
                PaitCoreModel(demo, BaseAppHelper, ParamHandler, response_model_list=[response.FileResponseModel]),
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
                    ParamHandler,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
            )
        exec_msg = e.value.args[0]
        assert "Please set redis`s param:decode_responses to True" in exec_msg

    def test_cache_name_param_set_gen(self) -> None:
        def demo(
            a: int = field.Query.i(extra_param_list=[CacheRespExtraParam()]),
            b: int = field.Query.i(extra_param_list=[CacheRespExtraParam()]),
            c: int = field.Query.i(),
        ) -> None:
            pass

        CacheResponsePluginManager = CacheResponsePlugin.build(redis=Redis(decode_responses=True))

        CacheResponsePluginManager.pre_load_hook(
            PaitCoreModel(
                demo,
                BaseAppHelper,
                ParamHandler,
                response_model_list=[response.JsonResponseModel, response.TextResponseModel],
            ),
        )
        assert CacheResponsePluginManager._kwargs["_cache_name_param_set"] == {"a", "b"}

    #
    # def test_not_found_redis(self) -> None:
    #     def demo() -> None:
    #         pass
    #     with pytest.raises(ValueError) as e:
    #         CacheResponsePlugin(
    #             next_plugin=lambda : None,
    #             pait_core_model=PaitCoreModel(
    #                 demo,
    #                 BaseAppHelper,
    #                 ParamHandler,
    #             ),
    #             name="demo",
    #             lock_name="demo:lock"
    #         )._get_redis()
    #
    #     exec_msg = e.value.args[0]
    #     assert exec_msg == "Not found redis client"


class TestCheckJsonPlugin:
    def test_pre_check_hook(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            CheckJsonRespPlugin.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    ParamHandler,
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
                PaitCoreModel(demo, BaseAppHelper, ParamHandler, response_model_list=[DemoCoreTestResponseModel]),
                {"get_pait_response_model": get_pait_response_model},
            )

        exec_msg: str = e.value.args[0]
        assert "pait_response_model must " in exec_msg


class TestMockPlugin:
    def test_not_found_response_model(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            MockPluginProtocol.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    ParamHandler,
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
                PaitCoreModel(demo, BaseAppHelper, ParamHandler, response_model_list=[response.JsonResponseModel]),
                {"pait_response_model": ""},
            )

        exec_msg: str = e.value.args[0]
        assert "Please use response_model_list param" in exec_msg

    def test_get_pait_response_model(self) -> None:
        def demo() -> None:
            pass

        kwargs: dict = MockPluginProtocol.pre_load_hook(
            PaitCoreModel(
                demo,
                BaseAppHelper,
                ParamHandler,
                response_model_list=[response.JsonResponseModel, response.TextResponseModel],
            ),
            {"get_pait_response_model": get_pait_response_model},
        )
        assert kwargs["pait_response_model"] == response.JsonResponseModel


class TestRequiredPlugin:
    def test_pre_load_with_init_param(self) -> None:
        def demo1() -> None:
            pass

        demo_core_model_1 = PaitCoreModel(
            demo1,
            BaseAppHelper,
            ParamHandler,
        )

        with pytest.raises(ValueError):
            RequiredPlugin.pre_load_hook(demo_core_model_1, {"required_dict": {"a": ["b", "c"]}})

        def demo2(
            a: int = field.Query.i(),
            b: int = field.Query.i(),
            c: int = field.Query.i(),
        ) -> None:
            pass

        demo_core_model_2 = PaitCoreModel(
            demo2,
            BaseAppHelper,
            ParamHandler,
        )
        RequiredPlugin.pre_load_hook(demo_core_model_2, {"required_dict": {"a": ["b", "c"]}})
        with pytest.raises(ValueError):
            RequiredPlugin.pre_load_hook(demo_core_model_2, {"required_dict": {"a": ["b", "c", "d"]}})

    def test_pre_load_with_extra_param(self) -> None:
        def demo(
            a: int = field.Query.i(extra_param_list=[]),
            b: int = field.Query.i(extra_param_list=[RequiredExtraParam(main_column="a")]),
            c: int = field.Query.i(extra_param_list=[RequiredExtraParam(main_column="a")]),
        ) -> None:
            pass

        demo_core_model = PaitCoreModel(
            demo,
            BaseAppHelper,
            ParamHandler,
        )
        kwargs_dict: dict = {"required_dict": {}}
        RequiredPlugin.pre_load_hook(demo_core_model, kwargs=kwargs_dict)
        assert kwargs_dict == {"required_dict": {"a": ["b", "c"]}}

        def demo1(
            a: int = field.Query.i(extra_param_list=[RequiredGroupExtraParam(group="aa", is_main=True)]),
            b: int = field.Query.i(extra_param_list=[RequiredGroupExtraParam(group="aa")]),
            c: int = field.Query.i(extra_param_list=[RequiredGroupExtraParam(group="aa")]),
        ) -> None:
            pass

        demo_core_model_1 = PaitCoreModel(
            demo1,
            BaseAppHelper,
            ParamHandler,
        )
        kwargs_dict = {"required_dict": {}}
        RequiredPlugin.pre_load_hook(demo_core_model_1, kwargs=kwargs_dict)
        assert kwargs_dict == {"required_dict": {"a": ["b", "c"]}}

    def test_check_param(self) -> None:
        def demo(
            a: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="a")]),
            a1: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="a")]),
            b: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="b")]),
            b1: int = field.Query.i(extra_param_list=[AtMostOneOfExtraParam(group="b")]),
        ) -> None:
            pass

        class FakePluginCoreModel:
            func = demo

        plugin = AtMostOneOfPlugin(
            lambda *args, **kwargs: None,
            FakePluginCoreModel(),  # type: ignore
            at_most_one_of_list=[["a", "a1"], ["b", "b1"]],
        )
        plugin.check_param(
            PluginContext(
                cbv_instance=None,
                app_helper=BaseAppHelper,  # type: ignore
                pait_core_model=FakePluginCoreModel(),  # type: ignore
                args=[],
                kwargs={"a": 1, "b": 1},
            )
        )

        with pytest.raises(CheckValueError):
            plugin.check_param(
                PluginContext(
                    cbv_instance=None,
                    app_helper=BaseAppHelper,  # type: ignore
                    pait_core_model=FakePluginCoreModel(),  # type: ignore
                    args=[],
                    kwargs={"a": 1, "a1": 1},
                )
            )


class TestUnifiedResponsePlugin:
    def test_pre_load_hook(self) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError):
            UnifiedResponsePluginProtocol.pre_load_hook(
                PaitCoreModel(
                    func=demo,
                    app_helper_class=BaseAppHelper,
                    param_handler_plugin=ParamHandler,
                ),
                kwargs={},
            )
        with pytest.raises(ValueError) as e:
            UnifiedResponsePluginProtocol.pre_load_hook(
                PaitCoreModel(
                    func=demo,
                    app_helper_class=BaseAppHelper,
                    param_handler_plugin=ParamHandler,
                ),
                kwargs={"get_pait_response_model": get_pait_response_model},
            )
        assert "The response model list cannot be empty, please add a response model to" in e.value.args[0]

        with pytest.raises(ValueError) as e:
            UnifiedResponsePluginProtocol.pre_load_hook(
                PaitCoreModel(
                    func=demo,
                    app_helper_class=BaseAppHelper,
                    param_handler_plugin=ParamHandler,
                    response_model_list=[FileResponseModel],
                ),
                kwargs={"get_pait_response_model": get_pait_response_model},
            )
        assert e.value.args[0] == "Not Support FileResponseModel"
