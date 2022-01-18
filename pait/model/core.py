import copy
import inspect
import logging
from typing import TYPE_CHECKING, Callable, List, Optional, Set, Tuple, Type

from pydantic import BaseConfig

from pait.model.response import PaitBaseResponseModel, PaitResponseModel
from pait.model.status import PaitStatus
from pait.param_handle import AsyncParamHandler, ParamHandler
from pait.plugin import PluginManager

if TYPE_CHECKING:
    from pait.app.base import BaseAppHelper


class PaitCoreModel(object):
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
    ):
        # pait
        self.app_helper_class: "Type[BaseAppHelper]" = app_helper_class
        self.func: Callable = func  # route func
        self.qualname: str = func.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]
        self.pait_id: str = f"{self.qualname}_{id(func)}"
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
        self.status: Optional[PaitStatus] = status or PaitStatus.undefined
        self.group: str = group or "root"  # Which group this interface belongs to
        self.tag: Tuple[str, ...] = tag or ("default",)  # Interface tag

        self._response_model_list: List[Type[PaitBaseResponseModel]] = []
        if response_model_list:
            self.add_response_model_list(response_model_list)

        # pait plugin
        self._plugin_list: List[PluginManager] = []
        self._post_plugin_list: List[PluginManager] = []
        self._plugin_manager_list: List[PluginManager] = []
        if inspect.iscoroutinefunction(self.func):
            self._param_handler_plugin: PluginManager = PluginManager(AsyncParamHandler)
        else:
            self._param_handler_plugin = PluginManager(ParamHandler)
        self._param_handler_plugin.cls_hook_by_core_model(self)
        self.add_plugin(plugin_list, post_plugin_list)

    @property
    def method_list(self) -> List[str]:
        return self._method_list

    @method_list.setter
    def method_list(self, method_list: List[str]) -> None:
        _temp_set: Set[str] = set(self._method_list) | set(method_list)
        _temp_set.difference_update(self.block_http_method_set)
        self._method_list = sorted(list(_temp_set))

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
    def plugin_list(self) -> List[PluginManager]:
        return self._plugin_manager_list

    def add_plugin(
        self, plugin_list: Optional[List[PluginManager]], post_plugin_list: Optional[List[PluginManager]]
    ) -> None:
        raw_plugin_list: List[PluginManager] = self._plugin_list
        raw_post_plugin_list: List[PluginManager] = self._post_plugin_list
        try:
            for plugin_manager in plugin_list or []:
                plugin_manager.cls_hook_by_core_model(self)
                if not plugin_manager.plugin_class.is_pre_core:
                    raise ValueError(f"{plugin_manager.plugin_class} is post plugin")
                self._plugin_list.append(plugin_manager)

            for plugin_manager in post_plugin_list or []:
                plugin_manager.cls_hook_by_core_model(self)
                if plugin_manager.plugin_class.is_pre_core:
                    raise ValueError(f"{plugin_manager.plugin_class} is pre plugin")
                self._post_plugin_list.append(plugin_manager)
        except Exception as e:
            self._plugin_list = raw_plugin_list
            self._post_plugin_list = raw_post_plugin_list
            raise e
        else:
            # In future version, it may be possible to switch plugins at runtime
            plugin_manager_list: List[PluginManager] = copy.deepcopy(
                self._plugin_list + [self._param_handler_plugin] + self._post_plugin_list
            )
            plugin_manager_list.reverse()
            self._plugin_manager_list = plugin_manager_list
