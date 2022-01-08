import inspect
from typing import Any, Type, Union

from pait.model.core import PaitCoreModel


class PluginProtocol(object):
    is_pre_core: bool = True
    pait_core_model: PaitCoreModel
    args: list
    kwargs: dict

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    @classmethod
    def check_cls_by_core_model(cls, pait_core_model: PaitCoreModel) -> None:
        pass

    def __post_init__(self, pait_core_model: PaitCoreModel, args: tuple, kwargs: dict) -> None:
        self.pait_core_model = pait_core_model
        self.args = list(args) or []
        self.kwargs = kwargs or {}


class BasePlugin(PluginProtocol):
    def call_next(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Failed to load PluginManager, please check the list of plugins")

    @classmethod
    def check_cls_by_core_model(cls, pait_core_model: PaitCoreModel) -> None:
        if inspect.iscoroutinefunction(pait_core_model.func):
            raise TypeError("PluginManager not support async func")

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.call_next(*args, **kwargs)


class BaseAsyncPlugin(PluginProtocol):
    async def call_next(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Failed to load PluginManager, please check the list of plugins")

    @classmethod
    def check_cls_by_core_model(cls, pait_core_model: PaitCoreModel) -> None:
        if not inspect.iscoroutinefunction(pait_core_model.func):
            raise TypeError("PluginManager only support async func")

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.call_next(*args, **kwargs)


_T = Union[BasePlugin, BaseAsyncPlugin]


class PluginManager(object):
    def __init__(self, plugin_class: Type[_T], *args: Any, **kwargs: Any):
        self.plugin_class: Type[_T] = plugin_class
        self._args: Any = args
        self._kwargs: Any = kwargs

    def check_plugin_cls_by_core_model(self, pait_core_model: PaitCoreModel) -> None:
        self.plugin_class.check_cls_by_core_model(pait_core_model)

    def get_plugin(self) -> _T:
        return self.plugin_class(*self._args, **self._kwargs)
