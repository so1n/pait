import pytest
from pytest_mock import MockFixture

from pait import core, g


class TestPaitCore:
    def test_pait_core(self) -> None:
        with pytest.raises(TypeError) as e:

            @core.pait("a")
            def demo() -> None:
                pass

        exec_msg: str = e.value.args[0]
        assert exec_msg.endswith("must be class")

    def test_pait_id_not_in_data(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.data.logging.warning")
        g.pait_data.add_route_info("fake_id", "/", {"get"}, "fake")
        patch.assert_called_once()

    def test_pait_id_in_data(self, mocker: MockFixture) -> None:
        pait_id: str = list(g.pait_data.pait_id_dict.keys())[0]
        g.pait_data.add_route_info(pait_id, "/", {"get"}, "fake")
        assert g.pait_data.pait_id_dict[pait_id].path == "/"
        assert g.pait_data.pait_id_dict[pait_id].method_list == ["get"]
        assert g.pait_data.pait_id_dict[pait_id].operation_id == "fake"
        assert g.pait_data
