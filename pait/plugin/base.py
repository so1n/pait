import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, List, Type, TypeVar, Union

if TYPE_CHECKING:
    from pait.model.context import ContextModel as PluginContext
    from pait.model.core import PaitCoreModel

    from pait.model.response import BaseResponseModel  # isort: skip

_PluginT = TypeVar("_PluginT", bound="PluginProtocol")
_NextPluginT = Union[_PluginT, Callable]
logger: logging.Logger = logging.getLogger(__name__)
GetPaitResponseModelFuncType = Callable[[List[Type["BaseResponseModel"]]], Type["BaseResponseModel"]]


class PluginProtocol(object):
    def __init__(self, next_plugin: _NextPluginT, pait_core_model: "PaitCoreModel", **kwargs: Any) -> None:
        """Direct init calls are not supported,
        so there is no need to write clearly in init what parameters are needed
        """
        self.next_plugin: _NextPluginT = next_plugin
        self.pait_core_model: "PaitCoreModel" = pait_core_model
        self.is_async_mode: bool = pait_core_model.param_handler_plugin.is_async_mode
        if kwargs:
            for k, v in kwargs.items():
                if getattr(self, k, None) is not None:
                    continue
                setattr(self, k, v)
        self.__post_init__(**kwargs)

    def __post_init__(self, **kwargs: Any) -> None:
        """Called after the `__init__` and used to initialize the plugin"""

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        """The hook that runs the check at add plugin to route. If the value of env's PAIT_IGNORE_PRE_CHECK is True,
        it will not be executed.

        Note:
            Failure to execute this stage will cause the plugin to fail to load, but will not affect the use of routes
        """

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        """The hook that runs the check at build plugin stack

        Note:
            Failure to execute this stage will cause the plugin to fail to load, but will affect the use of routes
        """
        return kwargs  # pragma: no cover

    @classmethod
    def build(cls, **kwargs: Any) -> "PluginManager[_PluginT]":
        """Factory function for generating plugins"""
        return PluginManager(cls, **kwargs)  # type: ignore

    def __call__(self, context: "PluginContext") -> Any:
        """The entry function called by the plugin."""
        if isinstance(self.next_plugin, PluginProtocol):
            return self.next_plugin(context)
        else:
            return self.next_plugin(*context.args, **context.kwargs)


class PrePluginProtocol(PluginProtocol):
    """Pre Plugin"""


class PostPluginProtocol(PluginProtocol):
    """Post Plugin"""


class PluginManager(Generic[_PluginT]):
    """
    A proxy for the Pait plugin, Ensure plugins referenced by each route function are isolated

    Note: The plug-in will expose the build method to the user,
        and the user does not need to call it directly `PluginManager`
    """

    def __init__(self, plugin_class: Type[_PluginT], **kwargs: Any):
        self.plugin_class = plugin_class
        self.plugin_kwargs = kwargs
        self._already_check = False

    def pre_check_hook(self, pait_core_model: "PaitCoreModel") -> None:
        if self._already_check:
            return
        self._already_check = True
        self.plugin_class.pre_check_hook(pait_core_model, self.plugin_kwargs)

    def pre_load_hook(self, pait_core_model: "PaitCoreModel") -> None:
        self.plugin_kwargs = self.plugin_class.pre_load_hook(pait_core_model, self.plugin_kwargs)

    def get_plugin(self, next_plugin: _NextPluginT, pait_core_model: "PaitCoreModel") -> _PluginT:
        return self.plugin_class(next_plugin, pait_core_model, **self.plugin_kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.plugin_class.__name__}>"
