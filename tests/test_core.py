from typing import Any, Type

import pytest
from pytest_mock import MockFixture

from pait import core, g
from pait.app.base import BaseAppHelper
from pait.model.core import PaitCoreModel
from pait.model.response import PaitBaseResponseModel


def demo() -> None:
    pass


app_name: str = "fake_name"


class FakeAppHelper(BaseAppHelper):
    RequestType = str
    FormType = int
    FileType = float
    HeaderType = type(None)


class TestPaitCore:
    def test_pait_core(self) -> None:
        def make_mock_response(pait_response: Type[PaitBaseResponseModel]) -> Any:
            pass

        with pytest.raises(TypeError) as e:

            @core.pait("a", make_mock_response)  # type: ignore
            def demo_() -> None:
                pass

        exec_msg: str = e.value.args[0]
        assert exec_msg.endswith("must be class")

        class Demo:
            pass

        with pytest.raises(TypeError) as e:

            @core.pait(Demo, make_mock_response)  # type: ignore
            def demo() -> None:
                pass

        exec_msg = e.value.args[0]
        assert "must sub " in exec_msg

    def test_pait_id_not_in_data(self, mocker: MockFixture) -> None:
        def make_mock_response(pait_response: Type[PaitBaseResponseModel]) -> Any:
            pass

        pait_core_model: PaitCoreModel = PaitCoreModel(demo, FakeAppHelper, make_mock_response)
        pait_id: str = pait_core_model.pait_id
        g.pait_data.register(app_name, pait_core_model)
        patch = mocker.patch("pait.data.logging.warning")
        g.pait_data.add_route_info(app_name, pait_id + "o", "/", "/", {"get"}, "fake", "")
        patch.assert_called_once()

    def test_pait_id_in_data(self) -> None:
        def make_mock_response(pait_response: Type[PaitBaseResponseModel]) -> Any:
            pass

        pait_core_model: PaitCoreModel = PaitCoreModel(demo, FakeAppHelper, make_mock_response)
        pait_id: str = pait_core_model.pait_id
        g.pait_data.register(app_name, pait_core_model)
        g.pait_data.add_route_info(app_name, pait_id, "/", "/", {"get"}, "fake", "")
        assert g.pait_data.pait_id_dict[app_name][pait_id].path == "/"
        assert g.pait_data.pait_id_dict[app_name][pait_id].method_list == ["get"]
        assert g.pait_data.pait_id_dict[app_name][pait_id].operation_id == "fake"
        assert g.pait_data
