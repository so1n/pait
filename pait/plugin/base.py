from typing import Any

from pait.model.core import PaitCoreModel


class PluginInitProtocol(object):
    pait_core_model: PaitCoreModel
    args: list
    kwargs: dict

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __post_init__(self, pait_core_model: PaitCoreModel, args: tuple, kwargs: dict) -> None:
        self.pait_core_model = pait_core_model
        self.args = list(args) or []
        self.kwargs = kwargs or {}


class BasePlugin(PluginInitProtocol):
    def call_next(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Failed to load Plugin, please check the list of plugins")

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.call_next(*args, **kwargs)


class BaseAsyncPlugin(PluginInitProtocol):
    async def call_next(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Failed to load Plugin, please check the list of plugins")

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.call_next(*args, **kwargs)
