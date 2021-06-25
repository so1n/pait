import pytest
from pytest_mock import MockFixture

from pait import core, g
from pait.model.core import PaitCoreModel


def demo() -> None:
    pass


pait_id: str = "fake_id"
app_name: str = "fake_name"


class TestPaitCore:
    def test_pait_core(self) -> None:
        with pytest.raises(TypeError) as e:

            @core.pait("a")  # type: ignore
            def demo_() -> None:
                pass

        exec_msg: str = e.value.args[0]
        assert exec_msg.endswith("must be class")

        class Demo:
            pass

        with pytest.raises(TypeError) as e:

            @core.pait(Demo)  # type: ignore
            def demo() -> None:
                pass

        exec_msg = e.value.args[0]
        assert "must sub " in exec_msg

    def test_pait_id_not_in_data(self, mocker: MockFixture) -> None:
        g.pait_data.register(app_name, PaitCoreModel(demo, pait_id))
        patch = mocker.patch("pait.data.logging.warning")
        g.pait_data.add_route_info(app_name, pait_id + "o", "/", {"get"}, "fake", "")
        patch.assert_called_once()

    def test_pait_id_in_data(self) -> None:
        g.pait_data.register(app_name, PaitCoreModel(demo, pait_id))
        g.pait_data.add_route_info(app_name, pait_id, "/", {"get"}, "fake", "")
        assert g.pait_data.pait_id_dict[app_name][pait_id].path == "/"
        assert g.pait_data.pait_id_dict[app_name][pait_id].method_list == ["get"]
        assert g.pait_data.pait_id_dict[app_name][pait_id].operation_id == "fake"
        assert g.pait_data
