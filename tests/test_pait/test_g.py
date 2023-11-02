from pait import g
from pait.app.base import BaseAppHelper
from pait.extra.config import apply_block_http_method_set
from pait.model.core import PaitCoreModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag
from pait.param_handle import ParamHandler


class TestG:
    def test_config_tag(self) -> None:
        tag = Tag(f"{__name__} test g")
        assert tag.name in g.config.tag_dict

    def test_sync_config_data_to_pait_core_model(self) -> None:
        demo_core_model = PaitCoreModel(
            lambda x: x, app_helper_class=BaseAppHelper, param_handler_plugin=ParamHandler, method_set={"HEAD", "GET"}
        )
        assert demo_core_model.method_list == ["GET", "HEAD"]
        g.pait_data.register(__name__, demo_core_model)
        g.config.init_config(status=PaitStatus.test, apply_func_list=[apply_block_http_method_set({"HEAD"})])
        assert demo_core_model.status is PaitStatus.test
        assert demo_core_model.method_list == ["GET"]
