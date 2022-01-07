from typing import Any

from pait.model.core import PaitCoreModel


class PluginInitProtocol(object):
    pait_core_model: PaitCoreModel
    args: list
    kwargs: dict

    def __post_init__(self, pait_core_model: PaitCoreModel, args: tuple, kwargs: dict) -> None:
        self.pait_core_model = pait_core_model
        self.args = list(args) or []
        self.kwargs = kwargs or {}


class BasePlugin(PluginInitProtocol):
    def call_next(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.call_next(*args, **kwargs)


class BaseAsyncPlugin(PluginInitProtocol):
    async def call_next(self, *args: Any, **kwargs: Any) -> Any:
        pass

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.call_next(*args, **kwargs)
