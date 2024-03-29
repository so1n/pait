from typing import TYPE_CHECKING, List, Optional, Type

import pytest
from pydantic import BaseConfig, BaseModel, Field

from pait.app.base import BaseAppHelper
from pait.extra import config
from pait.model.core import PaitCoreModel
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag
from pait.param_handle import BaseParamHandler, ParamHandler
from pait.plugin.base import PluginManager, PostPluginProtocol, PrePluginProtocol

if TYPE_CHECKING:
    from pait.model.config import APPLY_FN


class FakeAppHelper(BaseAppHelper):
    RequestType = str
    FormType = int
    FileType = float
    HeaderType = type(None)


def apply_default_pydantic_model_config(
    pydantic_model_config: Type[BaseConfig], match_rule: Optional["config.MatchRule"] = None
) -> "APPLY_FN":
    """pait route gen pydantic model default config"""

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if config._is_match(pait_core_model, match_rule):
            pait_core_model.pydantic_model_config = pydantic_model_config

    return _apply


class CustomerPaitCoreModel(PaitCoreModel):
    pydantic_model_config = BaseConfig


class TestApplyFun:
    def _demo_func(self) -> int:
        return 0

    _demo_func._pait_id = "fake_pait_id"  # type: ignore

    test_status_core_model: CustomerPaitCoreModel = CustomerPaitCoreModel(
        _demo_func, FakeAppHelper, ParamHandler, status=PaitStatus.test
    )
    test_group_core_model: CustomerPaitCoreModel = CustomerPaitCoreModel(
        _demo_func, FakeAppHelper, ParamHandler, group="test"
    )
    test_tag_core_model: CustomerPaitCoreModel = CustomerPaitCoreModel(
        _demo_func, FakeAppHelper, ParamHandler, tag=(Tag("test"), Tag("test_priority"))
    )
    test_path_core_model: CustomerPaitCoreModel = CustomerPaitCoreModel(_demo_func, FakeAppHelper, ParamHandler)
    test_method_core_model: CustomerPaitCoreModel = CustomerPaitCoreModel(
        _demo_func, FakeAppHelper, ParamHandler, tag=(Tag("test_priority"),)
    )

    core_model_list: List[CustomerPaitCoreModel] = [
        test_status_core_model,
        test_group_core_model,
        test_tag_core_model,
        test_path_core_model,
        test_method_core_model,
    ]
    for i in core_model_list:
        i.method_list = ["GET"]
        i.path = "/api/test"

    test_path_core_model.path = "/api/oktest"
    test_method_core_model.path = "/api/method-test"
    test_method_core_model.method_list = ["GET", "POST", "OPTIONS"]

    def test_apply_func_match(self) -> None:
        """test apply match and test apply_default_pydantic_model_config"""

        class DemoConfig(BaseConfig):
            title = "test"

        for _key, target, core_model in [
            ("status", PaitStatus.test, self.test_status_core_model),
            ("group", "test", self.test_group_core_model),
            ("tag", Tag("test"), self.test_tag_core_model),
            ("path", "/api/oktest", self.test_path_core_model),
            ("method_list", "OPTIONS", self.test_method_core_model),
        ]:
            for is_reverse in [True, False]:
                key: config.MatchKeyLiteral = _key if is_reverse is False else "!" + _key  # type: ignore

                for i in self.core_model_list:
                    apply_default_pydantic_model_config(DemoConfig, config.MatchRule(key=key, target=target))(i)

                if not is_reverse:
                    assert core_model.pydantic_model_config == DemoConfig
                    for i in self.core_model_list:
                        if i is core_model:
                            continue
                        assert i.pydantic_model_config != DemoConfig
                else:
                    assert core_model.pydantic_model_config != DemoConfig
                    for i in self.core_model_list:
                        if i is core_model:
                            continue
                        assert i.pydantic_model_config == DemoConfig

                # reset value
                for i in self.core_model_list:
                    apply_default_pydantic_model_config(BaseConfig)(i)

    def test_multi_apply_func_match(self) -> None:
        class DemoConfig(BaseConfig):
            title = "test"

        for key, target, core_model in [
            ("status", PaitStatus.test, self.test_status_core_model),
            ("group", "test", self.test_group_core_model),
            ("tag", Tag("test"), self.test_tag_core_model),
            ("path", "/api/oktest", self.test_path_core_model),
            ("method_list", "OPTIONS", self.test_method_core_model),
        ]:
            for is_and in [True, False]:
                for i in self.core_model_list:
                    if is_and:
                        apply_default_pydantic_model_config(
                            DemoConfig,
                            config.MatchRule(key=key, target=target)  # type: ignore
                            & config.MatchRule(key="method_list", target="DELETE"),  # type: ignore
                        )(i)
                    else:
                        apply_default_pydantic_model_config(
                            DemoConfig,
                            config.MatchRule(key=key, target=target)  # type: ignore
                            | config.MatchRule(key="method_list", target="DELETE"),  # type: ignore
                        )(i)
                if not is_and:
                    assert core_model.pydantic_model_config == DemoConfig
                    for i in self.core_model_list:
                        if i is core_model:
                            continue
                        assert i.pydantic_model_config != DemoConfig
                else:
                    for i in self.core_model_list:
                        assert i.pydantic_model_config != DemoConfig

                # reset value
                for i in self.core_model_list:
                    apply_default_pydantic_model_config(BaseConfig)(i)

    def test_multi_apply_func_match_priority(self) -> None:
        class DemoConfig(BaseConfig):
            title = "test"

        for i in self.core_model_list:
            apply_default_pydantic_model_config(
                DemoConfig,
                config.MatchRule(key="method_list", target="POST")
                & (
                    config.MatchRule(key="group", target="test")
                    | config.MatchRule(key="tag", target=Tag("test_priority"))
                ),
            )(i)

        for i in self.core_model_list:
            if i is self.test_method_core_model:
                assert i.pydantic_model_config == DemoConfig
            else:
                assert i.pydantic_model_config != DemoConfig

        # reset value
        for i in self.core_model_list:
            apply_default_pydantic_model_config(BaseConfig)(i)

        for i in self.core_model_list:
            apply_default_pydantic_model_config(
                DemoConfig,
                (config.MatchRule(key="method_list", target="POST") | config.MatchRule(key="group", target="test"))
                & (config.MatchRule(key="method_list", target="POST") | config.MatchRule(key="tag", target="test")),
            )(i)

        for i in self.core_model_list:
            if i is self.test_method_core_model:
                assert i.pydantic_model_config == DemoConfig
            else:
                assert i.pydantic_model_config != DemoConfig
            # reset value
        for i in self.core_model_list:
            apply_default_pydantic_model_config(BaseConfig)(i)

    def test_apply_extra_openapi_model(self) -> None:
        class DemoModel(BaseModel):
            a: int = Field()
            b: str = Field()

        for i in self.core_model_list:
            assert i.extra_openapi_model_list == []
            config.apply_extra_openapi_model(DemoModel)(i)
            assert i.extra_openapi_model_list == [DemoModel]

    def test_apply_response_model(self) -> None:
        class CoreResponseModel(BaseResponseModel):
            pass

        for i in self.core_model_list:
            assert i.response_model_list == []
            config.apply_response_model([JsonResponseModel])(i)
            assert i.response_model_list == [JsonResponseModel]

    def test_apply_block_http_method_set(self) -> None:
        for i in self.core_model_list:
            assert "GET" in i.method_list
            config.apply_block_http_method_set({"GET"})(i)
            assert "GET" not in i.method_list
        for i in self.core_model_list:
            with pytest.raises(ValueError):
                config.apply_block_http_method_set({"TEXT"})(i)

    def test_apply_mulit_plugin(self) -> None:
        class NotPrePlugin(PostPluginProtocol):
            pass

        class PrePlugin(PrePluginProtocol):
            pass

        post_pm: PluginManager = NotPrePlugin.build()
        pre_pm: PluginManager = PrePlugin.build()
        for i in self.core_model_list:
            assert len(i._plugin_list) == 0
            assert len(i._post_plugin_list) == 0
            config.apply_multi_plugin([lambda: post_pm, lambda: pre_pm])(i)
            assert len(i._plugin_list) == 1
            assert len(i._post_plugin_list) == 1
            assert i._plugin_list[0].plugin_class is pre_pm.plugin_class
            assert i._post_plugin_list[0].plugin_class is post_pm.plugin_class

    def test_apply_pre_depend(self) -> None:
        def demo_pre_depend() -> None:
            pass

        for i in self.core_model_list:
            assert i.pre_depend_list == []
            config.apply_pre_depend(demo_pre_depend)(i)
            assert i.pre_depend_list == [demo_pre_depend]

    def test_apply_param_handler(self) -> None:
        for i in self.core_model_list:
            raw_param_plugin = i.param_handler_plugin
            assert i.param_handler_plugin != BaseParamHandler
            config.apply_param_handler(BaseParamHandler)(i)
            assert i.param_handler_plugin == BaseParamHandler
            config.apply_param_handler(raw_param_plugin, config.MatchRule())(i)
            assert i.param_handler_plugin == raw_param_plugin

    def test_match_error_key(self) -> None:
        with pytest.raises(KeyError) as e:
            for i in self.core_model_list:
                config.apply_param_handler(BaseParamHandler, config.MatchRule(key="error key"))(i)  # type: ignore
        exec_msg: str = e.value.args[0]
        assert exec_msg == "match fail, not found key:error key"
        with pytest.raises(KeyError) as e:
            for i in self.core_model_list:
                config.apply_param_handler(BaseParamHandler, config.MatchRule(key="main_plugin"))(i)  # type: ignore
        exec_msg = e.value.args[0]
        assert exec_msg == "Not support key:main_plugin"
