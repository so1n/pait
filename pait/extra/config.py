from typing import TYPE_CHECKING, Callable, List, Optional, Set, Type

from pydantic import BaseConfig, BaseModel

from pait.model.response import PaitBaseResponseModel
from pait.plugin.base import PluginManager
from pait.util import http_method_tuple

if TYPE_CHECKING:
    from pait.model.config import APPLY_FN
    from pait.model.core import MatchRule, PaitCoreModel
    from pait.param_handle import BaseParamHandler


__all__ = [
    "apply_multi_plugin",
    "apply_extra_openapi_model",
    "apply_response_model",
    "apply_default_pydantic_model_config",
    "apply_block_http_method_set",
    "apply_pre_depend",
]


def apply_extra_openapi_model(
    extra_openapi_model: Type[BaseModel], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    """
    Add a default extre_openapi structure for routing handles
    """

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_rule):
            pait_core_model.extra_openapi_model_list = [extra_openapi_model]

    return _apply


def apply_response_model(
    response_model_list: List[Type[PaitBaseResponseModel]], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    """
    Add a default response structure for routing handles
    """
    for response_model in response_model_list:
        if response_model.is_core:
            raise ValueError(f"{response_model} is core response model can not set to default_response_model_list")

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_rule):
            pait_core_model.add_response_model_list(response_model_list)

    return _apply


def apply_default_pydantic_model_config(
    pydantic_model_config: Type[BaseConfig], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    """pait route gen pydantic model default config"""

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_rule):
            pait_core_model.pydantic_model_config = pydantic_model_config

    return _apply


def apply_block_http_method_set(
    block_http_method_set: Set[str], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    """
    Under normal circumstances, pait.load_app can obtain the http method of the routing handle.
     However, some application frameworks such as flask will automatically add optional http methods
     to the handle, which is great, but you may not want to use them in pait, and pait will not
     automatically recognize them, so you can use parameters to disable certain http method
    """
    for block_http_method in block_http_method_set:
        if block_http_method.lower() not in http_method_tuple:
            raise ValueError(f"Error http method: {block_http_method}")

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_rule):
            pait_core_model.block_http_method_set = block_http_method_set
            pait_core_model.method_list = pait_core_model.method_list

    return _apply


def apply_multi_plugin(
    plugin_manager_fn_list: List[Callable[[], PluginManager]], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_rule):
            pre_plugin_manager_list: List[PluginManager] = []
            post_plugin_manager_list: List[PluginManager] = []
            for plugin_manager_fn in plugin_manager_fn_list:
                plugin_manager: PluginManager = plugin_manager_fn()
                if plugin_manager.plugin_class.is_pre_core:
                    pre_plugin_manager_list.append(plugin_manager)
                else:
                    post_plugin_manager_list.append(plugin_manager)
            pait_core_model.add_plugin(pre_plugin_manager_list, post_plugin_manager_list)

    return _apply


def apply_pre_depend(pre_depend: Callable, match_rule: Optional["MatchRule"] = None) -> "APPLY_FN":
    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_rule):
            pait_core_model.pre_depend_list.append(pre_depend)

    return _apply


def apply_param_handler(
    param_handler_plugin: "Type[BaseParamHandler]", match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_rule):
            pait_core_model.param_handler_plugin = param_handler_plugin

    return _apply
