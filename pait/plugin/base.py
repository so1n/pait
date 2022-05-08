import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict, Generic, Type, TypeVar

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

_PluginT = TypeVar("_PluginT", bound="PluginProtocol")
logger: logging.Logger = logging.getLogger(__name__)


class PluginProtocol(object):
    is_pre_core: bool = True
    pait_core_model: "PaitCoreModel"
    args: list
    kwargs: dict

    _is_async_func: bool

    def __init__(self: "_PluginT", **kwargs: Any) -> None:
        """Direct init calls are not supported,
        so there is no need to write clearly in init what parameters are needed
        """
        if kwargs:
            for k, v in kwargs.items():
                if getattr(self, k, None) is not None:
                    continue
                setattr(self, k, v)

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        class_name: str = cls.__class__.__name__
        if class_name.startswith("Async"):
            logger.warning(
                f"Please use {class_name.replace('Async', '')}, {class_name} will remove on version 1.0"
            )  # pragma: no cover

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs["_is_async_func"] = inspect.iscoroutinefunction(pait_core_model.func)
        return kwargs  # pragma: no cover

    def __post_init__(self, pait_core_model: "PaitCoreModel", args: tuple, kwargs: dict) -> None:
        self.pait_core_model = pait_core_model
        self.args = list(args) or []
        self.kwargs = kwargs or {}

    @classmethod
    def build(cls, **kwargs: Any) -> "PluginManager[_PluginT]":
        return PluginManager(cls, **kwargs)  # type: ignore

    def call_next(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Failed to load Plugin, please check the list of plugins")  # pragma: no cover

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.call_next(*args, **kwargs)  # pragma: no cover


class PluginManager(Generic[_PluginT]):
    def __init__(self, plugin_class: Type[_PluginT], **kwargs: Any):
        self.plugin_class: Type[_PluginT] = plugin_class
        self._kwargs: Any = kwargs

    def pre_check_hook(self, pait_core_model: "PaitCoreModel") -> None:
        self.plugin_class.pre_check_hook(pait_core_model, self._kwargs)

    def pre_load_hook(self, pait_core_model: "PaitCoreModel") -> None:
        self._kwargs = self.plugin_class.pre_load_hook(pait_core_model, self._kwargs)

    def get_plugin(self) -> _PluginT:
        return self.plugin_class(**self._kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.plugin_class.__name__}>"
