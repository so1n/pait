import asyncio
import inspect
from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from pait.model.response import PaitBaseResponseModel
from pait.plugin.base import BaseAsyncPlugin, BasePlugin, PluginProtocol
from pait.util import get_pait_response_model

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class MockPluginInitProtocolMixin(PluginProtocol):
    is_pre_core: bool = False

    def __init__(self, pait_response: Type[PaitBaseResponseModel], **kwargs: Any):
        self.pait_response: Type[PaitBaseResponseModel] = pait_response
        super().__init__(**kwargs)

    @classmethod
    def cls_hook_by_core_model(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if not pait_core_model.response_model_list:
            raise RuntimeError(f"{pait_core_model.func} can not found response model")
        if "pait_response" in kwargs:
            raise ValueError("Please use response_model_list param")
        pait_response: Optional[Type[PaitBaseResponseModel]] = None
        if pait_core_model.enable_mock_response_filter_fn and pait_core_model.response_model_list:
            for _pait_response in pait_core_model.response_model_list:
                if pait_core_model.enable_mock_response_filter_fn(_pait_response):
                    pait_response = _pait_response
                    break

        if not pait_response:
            pait_response = get_pait_response_model(
                pait_core_model.response_model_list,
                target_pait_response_class=kwargs.pop("target_pait_response_class", False),
                find_core_response_model=kwargs.pop("find_coro_response_model", None),
            )
        kwargs["pait_response"] = pait_response
        return kwargs

    def mock_response(self) -> Any:
        raise NotImplementedError()

    def get_mock_response(self) -> Any:
        resp: Any = self.mock_response()
        # support async def
        if inspect.iscoroutinefunction(self.pait_core_model.func) and not inspect.iscoroutine(resp):
            future: asyncio.Future = asyncio.Future()
            future.set_result(resp)
            resp = future
        return resp


class BaseMockPlugin(MockPluginInitProtocolMixin, BasePlugin, ABC):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.get_mock_response()


class BaseAsyncMockPlugin(MockPluginInitProtocolMixin, BaseAsyncPlugin, ABC):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.get_mock_response()
