import re
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Set, Tuple, Type

from pydantic import BaseModel

from pait.model.response import BaseResponseModel
from pait.plugin.base import PluginManager, PrePluginProtocol
from pait.types import Literal
from pait.util import http_method_tuple

if TYPE_CHECKING:
    from pait.model.config import APPLY_FN
    from pait.model.core import PaitCoreModel
    from pait.param_handle import BaseParamHandler


__all__ = [
    "apply_multi_plugin",
    "apply_extra_openapi_model",
    "apply_response_model",
    "apply_block_http_method_set",
    "apply_pre_depend",
    "MatchRule",
]


MatchKeyLiteral = Literal[
    "all",
    "status",
    "group",
    "tag",
    "method_list",
    "path",
    "!status",
    "!group",
    "!tag",
    "!method_list",
    "!path",
]


class MatchRule(object):
    def __init__(self, key: MatchKeyLiteral = "all", target: Any = None):
        self.key: MatchKeyLiteral = key
        self.target: Any = target
        self._match_rule_list: List[Tuple[str, "MatchRule"]] = []

    def match(self, pait_core_model: "PaitCoreModel") -> bool:
        result: bool = self._match(pait_core_model)
        for method, match_rule in self._match_rule_list:
            if method == "or":
                result = result or match_rule.match(pait_core_model)
            elif method == "and":
                result = result and match_rule.match(pait_core_model)
        return result

    def _match(self, pait_core_model: "PaitCoreModel") -> bool:
        """By different attributes to determine whether to match with pait_core_model,
        if the key is `all` then match
        if the key is prefixed with ! then the result will be reversed
        """
        key: MatchKeyLiteral = self.key
        target: Any = self.target
        if key == "all":
            return True
        is_reverse: bool = False
        if key.startswith("!"):
            key = key[1:]  # type: ignore
            is_reverse = True

        value: Any = getattr(pait_core_model, key, ...)
        if value is ...:
            raise KeyError(f"match fail, not found key:{key}")
        if key in ("status", "group"):
            result: bool = value is target
        elif key in ("tag", "method_list"):
            result = target in value
        elif key == "path":
            result = bool(re.match(target, value))
        else:
            raise KeyError(f"Not support key:{key}")

        if is_reverse:
            return not result
        else:
            return result

    def __or__(self, other: "MatchRule") -> "MatchRule":
        self._match_rule_list.append(("or", other))
        return self

    def __and__(self, other: "MatchRule") -> "MatchRule":
        self._match_rule_list.append(("and", other))
        return self

    def __repr__(self) -> str:
        return f"<MatchRule object; key={self.key}, target={self.target} match_rule_list={self._match_rule_list}>"


def _is_match(pait_core_model: "PaitCoreModel", match_rule: Optional["MatchRule"]) -> bool:
    return not match_rule or match_rule.match(pait_core_model)


def apply_extra_openapi_model(
    extra_openapi_model: Type[BaseModel], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    """
    Add a default extre_openapi structure for routing handles
    """

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if _is_match(pait_core_model, match_rule):
            pait_core_model.extra_openapi_model_list = [extra_openapi_model]

    return _apply


def apply_response_model(
    response_model_list: List[Type[BaseResponseModel]], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    """
    Add a default response structure for routing handles
    """

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if _is_match(pait_core_model, match_rule):
            pait_core_model.add_response_model_list(response_model_list)

    return _apply


def apply_default_pydantic_basemodel(
    pydantic_basemodel: Type[BaseModel], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    """pait route gen pydantic model default pydantic base model"""

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if _is_match(pait_core_model, match_rule):
            pait_core_model.pydantic_basemodel = pydantic_basemodel

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
        if _is_match(pait_core_model, match_rule):
            pait_core_model.block_http_method_set = block_http_method_set
            pait_core_model.method_list = pait_core_model.method_list

    return _apply


def apply_multi_plugin(
    plugin_manager_fn_list: List[Callable[[], PluginManager]], match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if _is_match(pait_core_model, match_rule):
            pre_plugin_manager_list: List[PluginManager] = []
            post_plugin_manager_list: List[PluginManager] = []
            for plugin_manager_fn in plugin_manager_fn_list:
                plugin_manager: PluginManager = plugin_manager_fn()
                if issubclass(plugin_manager.plugin_class, PrePluginProtocol):
                    pre_plugin_manager_list.append(plugin_manager)
                else:
                    post_plugin_manager_list.append(plugin_manager)
            pait_core_model.add_plugin(pre_plugin_manager_list, post_plugin_manager_list)

    return _apply


def apply_pre_depend(pre_depend: Callable, match_rule: Optional["MatchRule"] = None) -> "APPLY_FN":
    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if _is_match(pait_core_model, match_rule):
            pait_core_model.pre_depend_list.append(pre_depend)

    return _apply


def apply_param_handler(
    param_handler_plugin: "Type[BaseParamHandler]", match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if _is_match(pait_core_model, match_rule):
            pait_core_model.param_handler_plugin = param_handler_plugin

    return _apply
