import inspect
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Set, Tuple, Type

from pydantic import BaseConfig, BaseModel

from pait.model.response import PaitBaseResponseModel, PaitResponseModel
from pait.model.status import PaitStatus
from pait.param_handle import AsyncParamHandler, BaseParamHandler, ParamHandler
from pait.plugin import PluginManager
from pait.types import Literal
from pait.util import ignore_pre_check

if TYPE_CHECKING:
    from pait.app.base import BaseAppHelper


__all__ = ["PaitCoreModel", "MatchRule", "MatchKeyLiteral", "ContextModel"]
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


@dataclass
class MatchRule(object):
    key: MatchKeyLiteral = "all"
    target: Any = None


@dataclass
class ContextModel(object):
    cbv_instance: Optional[Any]
    app_helper: "BaseAppHelper"


class PaitCoreModel(object):
    _param_handler_plugin: PluginManager["BaseParamHandler"]

    def __init__(
        self,
        func: Callable,
        app_helper_class: "Type[BaseAppHelper]",
        pre_depend_list: Optional[List[Callable]] = None,
        path: Optional[str] = None,
        openapi_path: Optional[str] = None,
        method_set: Optional[Set[str]] = None,
        operation_id: Optional[str] = None,
        func_name: Optional[str] = None,
        author: Optional[Tuple[str, ...]] = None,
        summary: Optional[str] = None,
        desc: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[str, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        plugin_list: Optional[List[PluginManager]] = None,
        post_plugin_list: Optional[List[PluginManager]] = None,
        param_handler_plugin: Optional[Type[BaseParamHandler]] = None,
        feature_code: str = "",
    ):
        # pait
        self.app_helper_class: "Type[BaseAppHelper]" = app_helper_class
        self.func: Callable = func  # route func
        # self.qualname: str = func.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]
        self.pait_id: str = f"{func.__qualname__}_{self.func_md5}"
        # Some functions have the same md5 as the name and need to be distinguished by the feature code
        if feature_code:
            self.pait_id = f"{feature_code}_{self.pait_id}"
        setattr(func, "_pait_id", self.pait_id)
        setattr(func, "pait_core_model", self)
        self.pre_depend_list: List[Callable] = pre_depend_list or []
        self.func_path: str = ""
        self.block_http_method_set: Set[str] = set()
        self.pydantic_model_config: Type[BaseConfig] = pydantic_model_config or BaseConfig

        # api doc
        self.path: str = path or ""  # request url path
        self.openapi_path: str = openapi_path or ""
        self._method_list: List[str] = sorted(list(method_set or set()))  # request method set
        self.func_name: str = func_name or func.__name__
        self.operation_id: str = operation_id or self.func_name  # route name
        self.author: Optional[Tuple[str, ...]] = author  # The main developer of this func
        self.summary: str = summary or ""
        self.desc: str = desc or func.__doc__ or ""  # desc of this func
        self.status: PaitStatus = status or PaitStatus.undefined
        self.group: str = group or "root"  # Which group this interface belongs to
        self.tag: Tuple[str, ...] = tag or ("default",)  # Interface tag
        self._extra_openapi_model_list: List[Type[BaseModel]] = []

        self._response_model_list: List[Type[PaitBaseResponseModel]] = []
        if response_model_list:
            self.add_response_model_list(response_model_list)

        # pait plugin
        self._plugin_list: List[PluginManager] = []
        self._post_plugin_list: List[PluginManager] = []
        self._plugin_manager_list: List[PluginManager] = []

        self.param_handler_plugin = param_handler_plugin  # type: ignore
        self.add_plugin(plugin_list, post_plugin_list)

    @property
    def param_handler_plugin(self) -> Type[BaseParamHandler]:
        return self._param_handler_plugin.plugin_class

    @param_handler_plugin.setter
    def param_handler_plugin(self, param_handler_plugin: Optional[Type[BaseParamHandler]]) -> None:
        if param_handler_plugin:
            self._param_handler_plugin = PluginManager(param_handler_plugin)
        elif inspect.iscoroutinefunction(self.func):
            self._param_handler_plugin = PluginManager(AsyncParamHandler)
        else:
            self._param_handler_plugin = PluginManager(ParamHandler)
        if not ignore_pre_check:
            self._param_handler_plugin.pre_check_hook(self)
        self._param_handler_plugin.pre_load_hook(self)
        if not self._plugin_manager_list:
            self.add_plugin([], [])

    @property
    def func_md5(self) -> str:
        from hashlib import md5

        h = md5()
        h.update(self.func.__code__.co_code)  # type: ignore
        return h.hexdigest()

    @property
    def method_list(self) -> List[str]:
        _temp_set: Set[str] = set(self._method_list.copy())
        _temp_set.difference_update(self.block_http_method_set)
        return sorted(list(_temp_set))

    @method_list.setter
    def method_list(self, method_list: List[str]) -> None:
        self._method_list = list(set(self._method_list) | set(method_list))

    @property
    def response_model_list(self) -> List[Type[PaitBaseResponseModel]]:
        return self._response_model_list

    def add_response_model_list(self, response_model_list: List[Type[PaitBaseResponseModel]]) -> None:
        for response_model in response_model_list:
            if response_model in self._response_model_list:
                continue
            if issubclass(response_model, PaitResponseModel):
                logging.warning(
                    f"Please replace {self.operation_id}'s response model {response_model}"
                    f" with {PaitBaseResponseModel}"
                )
            self._response_model_list.append(response_model)

    @property
    def extra_openapi_model_list(self) -> List[Type[BaseModel]]:
        return self._extra_openapi_model_list

    @extra_openapi_model_list.setter
    def extra_openapi_model_list(self, item: List[Type[BaseModel]]) -> None:
        self._extra_openapi_model_list.extend(item)

    @property
    def plugin_list(self) -> List[PluginManager]:
        return self._plugin_manager_list

    def match(self, match_rule: Optional[MatchRule] = None) -> bool:
        """By different attributes to determine whether to match with pait_core_model,
        if the key is `all` then match
        if the key is prefixed with ! then the result will be reversed
        """
        if not match_rule:
            match_rule = MatchRule()

        key: MatchKeyLiteral = match_rule.key
        target: Any = match_rule.target
        if key == "all":
            return True
        is_reverse: bool = False
        if key.startswith("!"):
            key = key[1:]  # type: ignore
            is_reverse = True

        value: Any = getattr(self, key, ...)
        if value is ...:
            raise KeyError(f"match fail, not found key:{key}")
        if key in ("status", "group"):
            result: bool = value is target
        elif key in ("tag", "method_list"):
            result = target in value
        elif key == "path":
            result = value.startswith(target)
        else:
            raise KeyError(f"Not support key:{key}")

        if is_reverse:
            return not result
        else:
            return result

    def add_plugin(
        self, plugin_list: Optional[List[PluginManager]], post_plugin_list: Optional[List[PluginManager]]
    ) -> None:
        raw_plugin_list: List[PluginManager] = self._plugin_list
        raw_post_plugin_list: List[PluginManager] = self._post_plugin_list
        try:
            for plugin_manager in plugin_list or []:
                if not plugin_manager.plugin_class.is_pre_core:
                    raise ValueError(f"{plugin_manager.plugin_class} is post plugin")
                if not ignore_pre_check:
                    plugin_manager.pre_check_hook(self)
                plugin_manager.pre_load_hook(self)
                self._plugin_list.append(plugin_manager)

            for plugin_manager in post_plugin_list or []:
                if plugin_manager.plugin_class.is_pre_core:
                    raise ValueError(f"{plugin_manager.plugin_class} is pre plugin")
                if not ignore_pre_check:
                    plugin_manager.pre_check_hook(self)
                plugin_manager.pre_load_hook(self)
                self._post_plugin_list.append(plugin_manager)
        except Exception as e:
            self._plugin_list = raw_plugin_list
            self._post_plugin_list = raw_post_plugin_list
            raise e
        else:
            # In future version, it may be possible to switch plugins at runtime
            plugin_manager_list: List[PluginManager] = (
                [i for i in self._plugin_list] + [self._param_handler_plugin] + [i for i in self._post_plugin_list]
            )
            # copy.deepcopy(
            #     self._plugin_list + [self._param_handler_plugin] + self._post_plugin_list
            # )
            plugin_manager_list.reverse()
            self._plugin_manager_list = plugin_manager_list
