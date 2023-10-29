import json
import traceback
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Type, Union

import pytest
from pydantic import BaseModel, Field

from example.common.request_model import SexEnum
from pait.app.base import BaseAppHelper
from pait.model import config as config_model
from pait.model import context, core, response, status, tag
from pait.model.core import PaitCoreModel
from pait.model.template import TemplateContext, TemplateVar
from pait.openapi.openapi import LinksModel
from pait.param_handle import BaseParamHandler, ParamHandler
from pait.plugin.base import PluginManager, PostPluginProtocol, PrePluginProtocol


class TestConfigModel:
    def test_repeat_config_init(self) -> None:
        config: config_model.Config = config_model.Config()
        config.author = "so1n"  # type: ignore
        assert config.author == "so1n"
        assert not config.initialized
        config.init_config()
        assert config.initialized

        with pytest.raises(RuntimeError) as e:
            config.init_config()

        exec_msg: str = e.value.args[0]
        assert "Can not set new value in runtime" in exec_msg
        with pytest.raises(RuntimeError) as e:
            config.author = "test"  # type: ignore

        exec_msg = e.value.args[0]
        assert "Can not set new value in runtime" in exec_msg

    def test_config_init(self) -> None:
        class DemoType(object):
            pass

        config: config_model.Config = config_model.Config()
        config.init_config(
            author=("so1n",),
            status=status.PaitStatus.undefined,
            json_type_default_value_dict={"demo": None},
            python_type_default_value_dict={DemoType: None},
        )
        assert config.author == ("so1n",)
        assert config.status == status.PaitStatus.undefined
        assert config.json_type_default_value_dict["demo"] is None
        assert config.python_type_default_value_dict[DemoType] is None

    def test_default_json_encoder(self) -> None:
        config: config_model.Config = config_model.Config()
        assert json.dumps(
            {
                "date": datetime.fromtimestamp(0).date(),
                "datetime": datetime.fromtimestamp(1600000000),
                "decimal": Decimal("0.0"),
                "enum": SexEnum.man,
                "int": 1,
                "str": "",
            },
            cls=config.json_encoder,
        ) == json.dumps(
            {"date": "1970-01-01", "datetime": 1600000000, "decimal": 0.0, "enum": "man", "int": 1, "str": ""}
        )


class TestContextModel:
    def test_state(self) -> None:
        ctx = context.ContextModel(None, None, None, [], {})  # type: ignore[arg-type]

        assert getattr(ctx, "state", None) is None
        with pytest.raises(AttributeError):
            assert ctx.get_form_state("aaa", 123) == 123

        ctx._init_state()
        assert ctx.get_form_state("aaa", 123) == 123

        with pytest.raises(KeyError):
            ctx.get_form_state("aaa")

        ctx.set_to_state("aaa", 123)
        assert ctx.get_form_state("aaa") == 123


def demo() -> None:
    pass


class TestPaitCoreModel:
    def test_get_core_model(self) -> None:
        code_model = core.PaitCoreModel(demo, BaseAppHelper, BaseParamHandler)
        assert core.get_core_model(demo) == code_model

        def not_init_demo() -> None:
            pass

        with pytest.raises(TypeError):
            core.get_core_model(not_init_demo)

    def test_pait_id_gen(self) -> None:
        assert core.PaitCoreModel(demo, BaseAppHelper, BaseParamHandler).pait_id == "tests.test_pait.test_model_demo"
        assert (
            core.PaitCoreModel(demo, BaseAppHelper, BaseParamHandler, feature_code="luluwa").pait_id
            == "luluwa_tests.test_pait.test_model_demo"
        )
        assert core.PaitCoreModel(demo, BaseAppHelper, BaseParamHandler).is_auto_gen_operation_id()

    def test_change_notify(self) -> None:
        change_dict: Dict[str, Any] = {}

        def listen_core_model_change(_core_model: core.PaitCoreModel, key: str, value: Any) -> None:
            change_dict[key] = value

        core_model = core.PaitCoreModel(demo, BaseAppHelper, BaseParamHandler)
        core_model.add_change_notify(listen_core_model_change)
        # test listen value change
        core_model.desc = "new desc"
        assert change_dict == {"desc": "new desc"}

        # The test does not listen for fields that begin with _
        core_model._mock_column = "mock"
        assert change_dict == {"desc": "new desc"}

        # test remove change
        core_model.remove_change_notify(listen_core_model_change)
        core_model.desc = "otehr desc"
        assert change_dict == {"desc": "new desc"}

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
            ParamHandler,
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


class TestLinksModel:
    def test_links_model(self) -> None:
        class DemoResponseModel(response.BaseResponseModel):
            response_data = ""

        # not found header
        with pytest.raises(KeyError) as e:
            LinksModel(DemoResponseModel, "$response.header.")._check_openapi_runtime_expr()

        exec_msg: str = e.value.args[0]
        assert "Can not found header key" in exec_msg

        # not base model response data
        with pytest.raises(RuntimeError) as e:  # type: ignore
            LinksModel(DemoResponseModel, "$response.body#")._check_openapi_runtime_expr()

        exec_msg = e.value.args[0]
        assert "response_data type is pydantic.Basemodel" in exec_msg

        # not support expr
        with pytest.raises(ValueError) as e:  # type: ignore
            LinksModel(DemoResponseModel, "$response.body")._check_openapi_runtime_expr()

        exec_msg = e.value.args[0]
        assert "Only support $response.headerXXX or $response.bodyXXX. " in exec_msg


class TestTagModel:
    def test_repeat_register_tag(self) -> None:
        tag.Tag("TestDemo", "test create tag")
        tag.Tag("TestDemo", "test create tag")

        with pytest.raises(KeyError):
            tag.Tag("TestDemo", "test create tag by other desc")


class TestResponseModel:
    def _test_dict_response_model(
        self, parent_response_class: Union[Type[response.JsonResponseModel], Type[response.XmlResponseModel]]
    ) -> None:
        def factory_value() -> str:
            return "mock"

        class DemoResponseModel(parent_response_class):  # type: ignore
            class DataModel(BaseModel):
                class SubModel(BaseModel):
                    normal_str_value: str = Field()
                    normal_int_value: int = Field()
                    normal_float_value: float = Field()
                    normal_bool_value: bool = Field()
                    normal_list_value: list = Field()
                    normal_dict_value: dict = Field()
                    normal_tuple_value: tuple = Field()
                    normal_datetime_value: datetime = Field()
                    normal_decimal_value: Decimal = Field()
                    normal_enum_value: SexEnum = Field()

                default_value: str = Field(default="default")
                default_factory_value: str = Field(default_factory=factory_value)
                example_value: str = Field(example="example_value")
                example_factory_value: str = Field(example=factory_value)
                sub_data: SubModel

            response_data: Type[BaseModel] = DataModel

        assert DemoResponseModel.get_default_dict() == {
            "default_value": "default",
            "default_factory_value": factory_value(),
            "example_value": "",
            "example_factory_value": "",
            "sub_data": {
                "normal_str_value": "",
                "normal_int_value": 0,
                "normal_float_value": 0.0,
                "normal_bool_value": True,
                "normal_list_value": [],
                "normal_dict_value": {},
                "normal_tuple_value": (),
                "normal_datetime_value": datetime.fromtimestamp(0),
                "normal_decimal_value": Decimal("0.0"),
                "normal_enum_value": SexEnum.man.value,  # type: ignore
            },
        }
        assert DemoResponseModel.get_example_value() == {
            "default_value": "default",
            "default_factory_value": factory_value(),
            "example_value": "example_value",
            "example_factory_value": factory_value(),
            "sub_data": {
                "normal_str_value": "",
                "normal_int_value": 0,
                "normal_float_value": 0.0,
                "normal_bool_value": True,
                "normal_list_value": [],
                "normal_dict_value": {},
                "normal_tuple_value": (),
                "normal_datetime_value": datetime.fromtimestamp(0),
                "normal_decimal_value": Decimal("0.0"),
                "normal_enum_value": SexEnum.man.value,  # type: ignore
            },
        }

    def test_json_response_model(self) -> None:
        for i in [response.JsonResponseModel, response.JsonResponseModel]:
            self._test_dict_response_model(i)  # type: ignore

    def test_xml_response_model(self) -> None:
        for i in [response.XmlResponseModel, response.XmlResponseModel]:
            self._test_dict_response_model(i)  # type: ignore


class TestTemplate:
    def test_template(self) -> None:
        template_var = TemplateVar(name="demo", default_value=1)
        assert template_var() == 1
        with TemplateContext({"demo": 2}):
            assert template_var() == 2
