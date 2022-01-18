import inspect
from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

_PluginT = TypeVar("_PluginT", bound="PluginProtocol")


class PluginProtocol(object):
    is_pre_core: bool = True
    pait_core_model: "PaitCoreModel"
    args: list
    kwargs: dict

    def __init__(self, **kwargs: Any) -> None:
        pass

    @classmethod
    def cls_hook_by_core_model(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        return kwargs  # pragma: no cover

    def __post_init__(self, pait_core_model: "PaitCoreModel", args: tuple, kwargs: dict) -> None:
        self.pait_core_model = pait_core_model
        self.args = list(args) or []
        self.kwargs = kwargs or {}


class BasePlugin(PluginProtocol):
    def call_next(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Failed to load PluginManager, please check the list of plugins")  # pragma: no cover

    @classmethod
    def cls_hook_by_core_model(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if inspect.iscoroutinefunction(pait_core_model.func):
            raise TypeError("PluginManager not support async func")
        return kwargs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.call_next(*args, **kwargs)  # pragma: no cover


class BaseAsyncPlugin(PluginProtocol):
    async def call_next(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Failed to load PluginManager, please check the list of plugins")  # pragma: no cover

    @classmethod
    def cls_hook_by_core_model(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if not inspect.iscoroutinefunction(pait_core_model.func):
            raise TypeError("PluginManager only support async func")
        return kwargs

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.call_next(*args, **kwargs)  # pragma: no cover


_T = Union[BasePlugin, BaseAsyncPlugin]


class PluginManager(object):
    def __init__(self, plugin_class: Type[_T], **kwargs: Any):
        self.plugin_class: Type[_T] = plugin_class
        self._kwargs: Any = kwargs

    def cls_hook_by_core_model(self, pait_core_model: "PaitCoreModel") -> None:
        self._kwargs = self.plugin_class.cls_hook_by_core_model(pait_core_model, self._kwargs)

    def get_plugin(self) -> _T:
        return self.plugin_class(**self._kwargs)
