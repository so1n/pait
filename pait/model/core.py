import logging
import traceback
import warnings
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Set, Tuple, Type, Union
from urllib.parse import quote_plus

from pydantic import BaseModel

from pait.exceptions import TipException
from pait.model.response import BaseResponseModel, PaitResponseModel, create_json_response_model
from pait.model.status import PaitStatus
from pait.model.tag import Tag
from pait.param_handle import BaseParamHandler
from pait.plugin import PluginManager, PluginProtocol, PostPluginProtocol, PrePluginProtocol
from pait.util import ImmutableDict, gen_tip_exc, ignore_pre_check

if TYPE_CHECKING:
    from pait.app.base import BaseAppHelper
    from pait.field import BaseRequestResourceField


__all__ = [
    "DefaultValue",
    "PaitCoreModel",
    "get_core_model",
    "AuthorOptionalType",
    "ChangeNotifyType",
    "DefaultFieldClassOptionalType",
    "DependListOptionalType",
    "DescOptionalType",
    "FuncNameOptionalType",
    "GroupOptionalType",
    "OperationIdOptionalType",
    "OptionalBoolType",
    "PluginListOptionalType",
    "PostPluginListOptionalType",
    "StatusOptionalType",
    "SummaryOptionalType",
    "TagOptionalType",
    "ResponseModelListOptionalType",
]

OptionalStrType = Optional[str]
OptionalBoolType = Optional[bool]
AuthorOptionalType = Optional[Tuple[str, ...]]
ChangeNotifyType = Callable[["PaitCoreModel", str, Any], None]
DefaultFieldClassOptionalType = Optional[Type["BaseRequestResourceField"]]
DependListOptionalType = Optional[List[Callable]]
DescOptionalType = OptionalStrType
FuncNameOptionalType = OptionalStrType
GroupOptionalType = OptionalStrType
OperationIdOptionalType = OptionalStrType
PluginListOptionalType = Optional[List[PluginManager[PrePluginProtocol]]]
PostPluginListOptionalType = Optional[List[PluginManager[PostPluginProtocol]]]
StatusOptionalType = Optional[PaitStatus]
SummaryOptionalType = OptionalStrType
TagOptionalType = Optional[Tuple[Tag, ...]]
ResponseModelListOptionalType = Optional[List[Type[Union[BaseResponseModel, BaseModel]]]]


def get_core_model(route: Callable) -> "PaitCoreModel":
    core_model: Optional["PaitCoreModel"] = getattr(route, "pait_core_model", None)
    if not core_model:
        raise TypeError(f"Routing function: {route} has not been wrapped by pait")
    return core_model


class DefaultValue(object):
    status: PaitStatus = PaitStatus.undefined
    group: str = "root"
    tag: Tuple[Tag, ...] = (Tag(name="default"),)
    tip_exception_class: Type[TipException] = TipException


class PaitCoreModel(object):
    _param_handler_plugin: PluginManager["BaseParamHandler"]
    _main_plugin: PluginProtocol

    def __init__(
        self,
        func: Callable,
        app_helper_class: "Type[BaseAppHelper]",
        param_handler_plugin: Type[BaseParamHandler],
        pre_depend_list: DependListOptionalType = None,
        path: Optional[str] = None,
        openapi_path: Optional[str] = None,
        method_set: Optional[Set[str]] = None,
        operation_id: OperationIdOptionalType = None,
        func_name: FuncNameOptionalType = None,
        author: AuthorOptionalType = None,
        summary: SummaryOptionalType = None,
        desc: DescOptionalType = None,
        status: StatusOptionalType = None,
        group: GroupOptionalType = None,
        tag: TagOptionalType = None,
        response_model_list: ResponseModelListOptionalType = None,
        default_field_class: DefaultFieldClassOptionalType = None,
        plugin_list: PluginListOptionalType = None,
        post_plugin_list: PostPluginListOptionalType = None,
        feature_code: Optional[str] = None,
        sync_to_thread: OptionalBoolType = None,
        tip_exception_class: Optional[Type[TipException]] = DefaultValue.tip_exception_class,
        **kwargs: Any,
    ):
        # pait
        self.app_helper_class = app_helper_class
        self.default_field_class = default_field_class
        self.func = func  # route func
        self.sync_to_thread = sync_to_thread
        self.tip_exception_class = tip_exception_class
        self.pait_id = f"{func.__module__}_{func.__qualname__}"
        # Some functions have the same md5 as the name and need to be distinguished by the feature code
        if feature_code:
            self.pait_id = f"{feature_code}_{self.pait_id}"
        setattr(func, "_pait_id", self.pait_id)
        setattr(func, "pait_core_model", self)
        self.pre_depend_list: List[Callable] = pre_depend_list or []
        self.func_path: str = self.func.__code__.co_filename  # type: ignore

        self.block_http_method_set: Set[str] = set()
        self.extra: dict = kwargs

        # api doc
        self.path: str = path or ""  # request url path
        self.openapi_path: str = openapi_path or ""
        self._method_list: List[str] = sorted(list(method_set or set()))  # request method set
        self.func_name: str = func_name or func.__qualname__
        self._operation_id: str = operation_id or self.pait_id
        self.author: AuthorOptionalType = author  # The main developer of this func
        self.summary: str = summary or ""
        self.desc: str = desc or func.__doc__ or ""  # desc of this func
        self.status: PaitStatus = status or DefaultValue.status
        self.group: str = group or DefaultValue.group  # Which group this interface belongs to
        self.tag: Tuple[Tag, ...] = tag or DefaultValue.tag  # Interface tag
        self._extra_openapi_model_list: List[Type[BaseModel]] = []
        self._response_model_list: List[Type[BaseResponseModel]] = []
        if response_model_list:
            self.add_response_model_list(response_model_list)

        # pait plugin
        self._need_build_plugin: bool = False
        self._plugin_list: List[PluginManager] = []
        self._post_plugin_list: List[PluginManager] = []
        self.param_handler_plugin = param_handler_plugin  # type: ignore
        self.add_plugin(plugin_list, post_plugin_list)

        # change notify
        self._change_notify_list: List[ChangeNotifyType] = []

        self.tag_label = ImmutableDict({i.name: i.label for i in tag if i.label}) if tag else ImmutableDict()

    def is_auto_gen_operation_id(self) -> bool:
        return self.operation_id == quote_plus(self.pait_id)

    def add_change_notify(self, callback: ChangeNotifyType) -> None:
        self._change_notify_list.append(callback)

    def remove_change_notify(self, callback: ChangeNotifyType) -> None:
        self._change_notify_list.remove(callback)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            return super().__setattr__(key, value)

        change_notify_list: List[ChangeNotifyType] = self.__dict__.get("_change_notify_list", [])
        if change_notify_list:
            for callback in self._change_notify_list:
                callback(self, key, value)
        return super().__setattr__(key, value)

    @property
    def operation_id(self) -> str:
        return self._operation_id

    @operation_id.setter
    def operation_id(self, operation_id: str) -> None:
        self._operation_id = quote_plus(operation_id)

    @property
    def param_handler_pm(self) -> PluginManager:
        return self._param_handler_plugin

    @property
    def param_handler_plugin(self) -> Type[BaseParamHandler]:
        return self._param_handler_plugin.plugin_class

    @param_handler_plugin.setter
    def param_handler_plugin(self, param_handler_plugin: Type[BaseParamHandler]) -> None:
        if hasattr(param_handler_plugin, "tip_exception_class"):
            suggest_use_msg = (
                "Suggest use @pait(tip_exception_class=xxx) or config.init_config(tip_exception_class=xxx)"
            )
            warnings.warn(
                "The tip_exception_class of the param_handler_plugin will deprecation after version 2.0.0,"
                f" {suggest_use_msg}",
                DeprecationWarning,
                stacklevel=2,
            )
            if self.tip_exception_class is not DefaultValue.tip_exception_class:
                raise ValueError(f"There are multiple method settings `tip_exception_class` param, {suggest_use_msg}")
            self.tip_exception_class = getattr(param_handler_plugin, "tip_exception_class", None)
        try:
            pm = PluginManager(param_handler_plugin)
            if not ignore_pre_check:
                pm.pre_check_hook(self)
        except Exception as e:
            raise gen_tip_exc(
                self.func,
                RuntimeError(f"set param plugin error: {e}" + "\n\n" + traceback.format_exc()),
                tip_exception_class=self.tip_exception_class,
            ) from e
        self._param_handler_plugin = pm
        self._need_build_plugin = True

    @property
    def method_list(self) -> List[str]:
        _temp_set: Set[str] = set(self._method_list.copy())
        _temp_set.difference_update(self.block_http_method_set)
        return sorted(list(_temp_set))

    @method_list.setter
    def method_list(self, method_list: List[str]) -> None:
        self._method_list = list(set(self._method_list) | set(method_list))

    @property
    def openapi_method_list(self) -> List[str]:
        return [i.lower() for i in self.method_list]

    @property
    def response_model_list(self) -> List[Type[BaseResponseModel]]:
        return self._response_model_list

    def add_response_model_list(self, response_model_list: List[Type[Union[BaseResponseModel, BaseModel]]]) -> None:
        for response_model in response_model_list:
            if issubclass(response_model, BaseModel):
                response_model = create_json_response_model(response_model)
            if response_model in self._response_model_list:
                continue
            if issubclass(response_model, PaitResponseModel):
                logging.warning(  # pragma: no cover
                    f"Please replace {self.operation_id}'s response model {response_model}" f" with {BaseResponseModel}"
                )
            self._response_model_list.append(response_model)

    @property
    def extra_openapi_model_list(self) -> List[Type[BaseModel]]:
        return self._extra_openapi_model_list

    @extra_openapi_model_list.setter
    def extra_openapi_model_list(self, item: List[Type[BaseModel]]) -> None:
        self._extra_openapi_model_list.extend(item)

    @property
    def main_plugin(self) -> PluginProtocol:
        return self._main_plugin

    def build_plugin_stack(self) -> None:
        plugin_manager_list: List[PluginManager] = (
            self._plugin_list + [self._param_handler_plugin] + self._post_plugin_list
        )
        for plugin_manager in plugin_manager_list:
            plugin_manager.pre_load_hook(self)

        self._main_plugin = self.func  # type: ignore
        for plugin_manager in reversed(plugin_manager_list):
            self._main_plugin = plugin_manager.get_plugin(self._main_plugin, self)
        self._need_build_plugin = False

    def build(self) -> None:
        """Currently, only plugins need to build, and other features may be added in the future,
        and they also need to build, so the build method is kept here"""
        if self._need_build_plugin:
            self.build_plugin_stack()

    def add_plugin(
        self,
        plugin_list: Optional[List[PluginManager[PrePluginProtocol]]],
        post_plugin_list: Optional[List[PluginManager[PostPluginProtocol]]],
    ) -> None:
        wait_add_plugin_list = []
        wait_add_post_plugin_list = []
        try:
            for plugin_manager in plugin_list or []:
                if not issubclass(plugin_manager.plugin_class, PrePluginProtocol):
                    raise ValueError(f"{plugin_manager.plugin_class} is post plugin")
                if not ignore_pre_check:
                    plugin_manager.pre_check_hook(self)
                wait_add_plugin_list.append(plugin_manager)

            for post_plugin_manager in post_plugin_list or []:
                if not issubclass(post_plugin_manager.plugin_class, PostPluginProtocol):
                    raise ValueError(f"{post_plugin_manager.plugin_class} is pre plugin")
                if not ignore_pre_check:
                    post_plugin_manager.pre_check_hook(self)
                wait_add_post_plugin_list.append(post_plugin_manager)
        except Exception as e:
            raise gen_tip_exc(
                self.func,
                RuntimeError(f"{self.func} add plugin error" + "\n\n" + traceback.format_exc()),
                tip_exception_class=self.tip_exception_class,
            ) from e
        else:
            self._need_build_plugin = True
            self._plugin_list.extend(wait_add_plugin_list)
            self._post_plugin_list.extend(wait_add_post_plugin_list)
