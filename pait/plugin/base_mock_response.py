import asyncio
import inspect
from abc import ABC
from typing import Any, Optional, Type

from pait.model.response import PaitBaseResponseModel
from pait.plugin.base import BaseAsyncPlugin, BasePlugin, PluginProtocol
from pait.util import get_pait_response_model


class MockPluginInitProtocolMixin(PluginProtocol):
    def __init__(
        self,
        find_coro_response_model: bool = False,
        target_pait_response_class: Optional[Type["PaitBaseResponseModel"]] = None,
        **kwargs: Any,
    ):
        self.find_coro_response_model: bool = find_coro_response_model
        self.target_pait_response_class: Optional[Type["PaitBaseResponseModel"]] = target_pait_response_class
        super().__init__(**kwargs)

    def mock_response(self, pait_response: Type[PaitBaseResponseModel]) -> Any:
        raise NotImplementedError()

    def get_mock_response(self, *args: Any, **kwargs: Any) -> Any:
        if not self.pait_core_model.response_model_list:
            raise RuntimeError(f"{self.pait_core_model.func} can not found response model")
        pait_response: Optional[Type[PaitBaseResponseModel]] = None
        if self.pait_core_model.enable_mock_response_filter_fn:
            for _pait_response in self.pait_core_model.response_model_list:
                if self.pait_core_model.enable_mock_response_filter_fn(_pait_response):
                    pait_response = _pait_response
                    break

        if not pait_response:
            pait_response = get_pait_response_model(
                self.pait_core_model.response_model_list,
                target_pait_response_class=self.target_pait_response_class,
                find_core_response_model=self.find_coro_response_model,
            )

        resp: Any = self.mock_response(pait_response)
        # support async def
        if inspect.iscoroutinefunction(self.pait_core_model.func) and not inspect.iscoroutine(resp):
            future: asyncio.Future = asyncio.Future()
            future.set_result(resp)
            resp = future
        return resp


class BaseMockPlugin(BasePlugin, MockPluginInitProtocolMixin, ABC):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.get_mock_response(*args, **kwargs)


class BaseAsyncMockPlugin(BaseAsyncPlugin, MockPluginInitProtocolMixin, ABC):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.get_mock_response(*args, **kwargs)
