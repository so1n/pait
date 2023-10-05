import pytest
from pytest_mock import MockFixture

from pait import core, g
from pait.app.base import BaseAppHelper
from pait.model.core import PaitCoreModel, get_core_model
from pait.model.response import JsonResponseModel
from pait.param_handle import ParamHandler
from tests.util import FakeAppHelper


def demo() -> None:
    pass


app_name: str = "fake_name"


class DemoPait(core.Pait):
    app_helper_class = BaseAppHelper


class TestPaitCore:
    def test_pait_not_set_app_helper_class(self) -> None:
        with pytest.raises(ValueError) as e:
            core.Pait()

        exec_msg: str = e.value.args[0]
        assert exec_msg == (
            "Please specify the value of the app_helper_class parameter, you can refer to `pait.app.xxx`"
        )

    def test_pait_set_error_app_helper_class(self) -> None:
        class Demo:
            pass

        class TestPait1(core.Pait):
            app_helper_class = object()  # type: ignore

        with pytest.raises(TypeError) as e:
            TestPait1()

        exec_msg: str = e.value.args[0]
        assert exec_msg.endswith("must be class")

        class TestPait2(core.Pait):
            app_helper_class = Demo  # type: ignore

        with pytest.raises(TypeError) as e:
            TestPait2()

        exec_msg = e.value.args[0]
        assert "must sub " in exec_msg

    def test_pait_id_not_in_data(self, mocker: MockFixture) -> None:
        pait_core_model: PaitCoreModel = PaitCoreModel(demo, FakeAppHelper, ParamHandler)
        pait_id: str = pait_core_model.pait_id
        g.pait_data.register(app_name, pait_core_model)
        patch = mocker.patch("pait.data.logging.warning")
        g.pait_data.get_core_model(app_name, pait_id + "o", "/", "/", {"get"}, "fake")
        patch.assert_called_once()

    def test_pait_id_in_data(self) -> None:
        pait_core_model: PaitCoreModel = PaitCoreModel(demo, FakeAppHelper, ParamHandler)
        pait_id: str = pait_core_model.pait_id
        assert g.pait_data
        g.pait_data.register(app_name, pait_core_model)
        pait_code_model = g.pait_data.get_core_model(app_name, pait_id, "/", "/", {"get"}, "fake")
        assert pait_code_model
        assert pait_code_model.path == "/"
        assert pait_code_model.method_list == ["get"]
        assert pait_code_model.operation_id == "fake"

    def test_extra_param(self) -> None:
        # Compatible with the use of older versions
        demo_pait = DemoPait(extra_a=1, extra_b=2)  # type: ignore
        assert demo_pait.param_kwargs["extra"]["extra_a"] == 1
        assert demo_pait.param_kwargs["extra"]["extra_b"] == 2

        # Usage after version 1.1
        demo_pait = DemoPait(extra={"extra_a": 1, "extra_b": 2})
        assert demo_pait.param_kwargs["extra"]["extra_a"] == 1
        assert demo_pait.param_kwargs["extra"]["extra_b"] == 2

    def test_pre_load_cbv_not_support_key(self) -> None:
        class Demo: ...

        for key in (
            "sync_to_thread",
            "feature_code",
            "plugin_list",
            "post_plugin_list",
            "param_handler_plugin",
            "name",
            "operation_id",
        ):
            with pytest.raises(ValueError) as e:
                core.Pait.pre_load_cbv(Demo, **{key: "test"})  # type: ignore

            exec_msg = e.value.args[0]
            assert f"{key} can't be used in pre_load_cbv" in exec_msg

    def test_pre_load_cbv_support_key(self) -> None:
        from pait.field import Json, Query
        from pait.model.core import DefaultValue
        from pait.model.response import HtmlResponseModel, XmlResponseModel
        from pait.model.status import PaitStatus
        from pait.model.tag import Tag
        from pait.plugin.at_most_one_of import AtMostOneOfPlugin
        from pait.plugin.check_json_resp import CheckJsonRespPlugin

        demo_pait = DemoPait()

        def pre_depend_1() -> None:
            pass

        def pre_depend_2() -> None:
            pass

        def pre_depend_3() -> None:
            pass

        tag1, tag2, tag3 = Tag("tag1"), Tag("tag2"), Tag("tag3")
        for key, value, attr in [
            ("default_field_class", (Query, Json), ""),
            ("pre_depend_list", ([pre_depend_1], [pre_depend_2]), ""),
            ("author", ("author_1", "author_2"), ""),
            ("desc", ("desc_1", "desc_2"), ""),
            ("summary", ("summary_1", "summary_2"), ""),
            ("status", (PaitStatus.test, PaitStatus.dev), ""),
            ("group", ("group_1", "group_2"), ""),
            ("tag", ((tag1,), (tag2,)), ""),
            ("response_model_list", ([HtmlResponseModel], [JsonResponseModel]), ""),
            (
                "append_pre_depend_list",
                (
                    [],
                    [pre_depend_3],
                ),
                "",
            ),
            (
                "append_author",
                (
                    tuple(),
                    ("author_3",),
                ),
                "",
            ),
            (
                "append_tag",
                (
                    tuple(),
                    (tag3,),
                ),
                "",
            ),
            (
                "append_response_model_list",
                (
                    [],
                    [XmlResponseModel],
                ),
                "",
            ),
            (
                "append_plugin_list",
                (
                    [],
                    [CheckJsonRespPlugin.build()],
                ),
                "_plugin_list",
            ),
            (
                "append_post_plugin_list",
                (
                    [],
                    [AtMostOneOfPlugin.build()],
                ),
                "_post_plugin_list",
            ),
        ]:
            first_value, pre_load_value = value
            if not attr:
                attr = key

            extra = {}
            if key == "append_plugin_list":
                extra["response_model_list"] = [JsonResponseModel]

            class Demo:
                @demo_pait(**{key: first_value, "feature_code": key, **extra})  # type: ignore
                def get(
                    self,
                ) -> None:
                    pass

                @demo_pait(**{"feature_code": key, **extra})  # type: ignore
                def post(
                    self,
                ) -> None:
                    pass

            demo_pait.pre_load_cbv(Demo, **{key: pre_load_value})  # type: ignore
            if not key.startswith("append"):
                assert getattr(get_core_model(Demo.get), attr) == first_value
                assert getattr(get_core_model(Demo.post), attr) == pre_load_value
            else:
                attr = attr.replace("append_", "")

                assert set(first_value + pre_load_value).issubset(  # type: ignore
                    set(getattr(get_core_model(Demo.get), attr))  # type: ignore
                )
                # assert getattr(get_core_model(Demo.get), attr) == first_value + pre_load_value
                if not pre_load_value:
                    default_value = getattr(DefaultValue, attr, None)
                    if default_value:
                        assert getattr(get_core_model(Demo.post), attr) is default_value
                    else:
                        assert not getattr(get_core_model(Demo.post), attr)
                else:
                    assert set(pre_load_value).issubset(set(getattr(get_core_model(Demo.post), attr)))  # type: ignore
