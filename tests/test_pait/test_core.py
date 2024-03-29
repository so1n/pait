import pytest
from pytest_mock import MockFixture

from pait import core, g
from pait.app.base import BaseAppHelper
from pait.model.core import PaitCoreModel
from pait.param_handle import ParamHandler


def demo() -> None:
    pass


app_name: str = "fake_name"


class FakeAppHelper(BaseAppHelper):
    RequestType = str
    FormType = int
    FileType = float
    HeaderType = type(None)


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

    def test_pait_response_list(self) -> None:
        from pait.app.base import BaseAppHelper

        class MyPait(core.Pait):
            app_helper_class = BaseAppHelper

        from pait.model.response import BaseResponseModel

        demo_core = MyPait()
        assert not demo_core.response_model_list
        demo_core.response_model_list.append(BaseResponseModel)
        assert len(demo_core.response_model_list) == 1
