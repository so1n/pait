from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Type

from pait.model.response import PaitBaseResponseModel
from pait.plugin.base import BaseAsyncPlugin, BasePlugin, PluginProtocol
from pait.util import get_pait_response_model

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class MockPluginInitProtocolMixin(PluginProtocol):
    is_pre_core: bool = False

    def __init__(self, pait_response_model: Type[PaitBaseResponseModel], **kwargs: Any):
        self.pait_response_model: Type[PaitBaseResponseModel] = pait_response_model
        super().__init__(**kwargs)

    @classmethod
    def cls_hook_by_core_model(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        super().cls_hook_by_core_model(pait_core_model, kwargs)
        if not pait_core_model.response_model_list:
            raise RuntimeError(f"{pait_core_model.func} can not found response model")
        if "pait_response_model" in kwargs:
            raise RuntimeError("Please use response_model_list param")
        pait_response: Optional[Type[PaitBaseResponseModel]] = None
        enable_mock_response_filter_fn: Optional[Callable] = kwargs.pop("enable_mock_response_filter_fn", None)
        if enable_mock_response_filter_fn and pait_core_model.response_model_list:
            for _pait_response in pait_core_model.response_model_list:
                if enable_mock_response_filter_fn(_pait_response):
                    pait_response = _pait_response
                    break

        if not pait_response:
            pait_response = get_pait_response_model(
                pait_core_model.response_model_list,
                target_pait_response_class=kwargs.pop("target_pait_response_class", False),
                find_core_response_model=kwargs.pop("find_coro_response_model", None),
            )
        kwargs["pait_response_model"] = pait_response
        return kwargs

    def mock_response(self) -> Any:
        raise NotImplementedError()

    def get_mock_response(self) -> Any:
        return self.mock_response()


class BaseMockPlugin(MockPluginInitProtocolMixin, BasePlugin, ABC):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.get_mock_response()


class BaseAsyncMockPlugin(MockPluginInitProtocolMixin, BaseAsyncPlugin, ABC):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.get_mock_response()
