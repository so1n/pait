from pait.app.base import BaseAppHelper
from pait.data import PaitCoreProxyModel
from pait.model.core import PaitCoreModel
from pait.model.response import BaseResponseModel
from pait.param_handle import ParamHandler


class TestPaitCoreProxyModel:
    def test_get_attr(self) -> None:
        core_model = PaitCoreModel(lambda x: x, BaseAppHelper, ParamHandler)
        proxy_core = PaitCoreProxyModel(core_model, "gululu")
        assert core_model.path == proxy_core.path

        assert core_model.operation_id != proxy_core.operation_id
        proxy_core.response_model_list.append(BaseResponseModel)  # type: ignore
        assert core_model.response_model_list != proxy_core.response_model_list
        assert PaitCoreProxyModel.get_core_model(proxy_core) is core_model
