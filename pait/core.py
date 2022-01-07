import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseConfig

from pait.app.base import BaseAppHelper
from pait.g import config, pait_data
from pait.model.core import PaitCoreModel
from pait.model.response import PaitBaseResponseModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag
from pait.model.util import sync_config_data_to_pait_core_model
from pait.param_handle import AsyncParamHandler, ParamHandler
from pait.plugin.base import BaseAsyncPlugin, BasePlugin
from pait.util import get_func_sig

_AppendT = TypeVar("_AppendT", list, tuple)
_PaitT = TypeVar("_PaitT", bound="Pait")
_PluginT = Union[BasePlugin, BaseAsyncPlugin]
TagT = Union[str, Tag]
PluginParamType = Tuple[Union[Type[BasePlugin], Type[BaseAsyncPlugin]], tuple, dict]


class Pait(object):
    app_helper_class: "Type[BaseAppHelper]"
    make_mock_response_fn: staticmethod  # real type hints: Callable[[Type[PaitBaseResponseModel]], Any]]

    def __init__(
        self,
        make_mock_response_fn: Optional[Callable[[Type[PaitBaseResponseModel]], Any]] = None,
        enable_mock_response: bool = False,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        at_most_one_of_list: Optional[List[List[str]]] = None,
        required_by: Optional[Dict[str, List[str]]] = None,
        # doc
        author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[TagT, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        plugin_list: Optional[List[PluginParamType]] = None,
    ):

        check_cls_param_list: List[str] = ["app_helper_class", "make_mock_response_fn"]
        for cls_param in check_cls_param_list:
            if not getattr(self, cls_param, None):
                raise ValueError(
                    f"Please specify the value of the {cls_param} parameter, you can refer to `pait.app.xxx`"
                )
        if not isinstance(self.app_helper_class, type):
            raise TypeError(f"{self.app_helper_class} must be class")
        if not issubclass(self.app_helper_class, BaseAppHelper):
            raise TypeError(f"{self.app_helper_class} must sub from {BaseAppHelper.__class__.__name__}")
        if getattr(self.make_mock_response_fn, "__self__", None):
            raise TypeError(
                "Set error make_mock_response_fn, should use `staticmethod` func. "
                "like `make_mock_response_fn = staticmethod(make_mock_response)`"
            )

        self._make_mock_response_fn: Callable[[Type[PaitBaseResponseModel]], Any] = (
            make_mock_response_fn or self.make_mock_response_fn
        )
        self._enable_mock_response: bool = enable_mock_response
        self._pydantic_model_config: Optional[Type[BaseConfig]] = pydantic_model_config
        # param check
        self._pre_depend_list: Optional[List[Callable]] = pre_depend_list
        self._at_most_one_of_list: Optional[List[List[str]]] = at_most_one_of_list
        self._required_by: Optional[Dict[str, List[str]]] = required_by
        # doc
        self._author: Optional[Tuple[str, ...]] = author
        self._desc: Optional[str] = desc
        self._summary: Optional[str] = summary
        self._name: Optional[str] = name
        self._status: Optional[PaitStatus] = status
        self._group: Optional[str] = group
        self._tag: Optional[Tuple[TagT, ...]] = tag
        self._response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = response_model_list
        self._plugin_list: Optional[List[PluginParamType]] = plugin_list

    @staticmethod
    def _append_data(
        target_container: Optional[_AppendT],
        append_container: Optional[_AppendT],
        self_container: Optional[_AppendT],
    ) -> Optional[_AppendT]:
        if append_container:
            return append_container + (self_container or append_container.__class__())
        else:
            return target_container or self_container

    def create_sub_pait(
        self: _PaitT,
        make_mock_response_fn: Callable[[Type[PaitBaseResponseModel]], Any] = None,
        enable_mock_response: bool = False,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        append_pre_depend_list: Optional[List[Callable]] = None,
        at_most_one_of_list: Optional[List[List[str]]] = None,
        append_at_most_one_of_list: Optional[List[List[str]]] = None,
        required_by: Optional[Dict[str, List[str]]] = None,
        append_required_by: Optional[Dict[str, List[str]]] = None,
        # doc
        author: Optional[Tuple[str, ...]] = None,
        append_author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[TagT, ...]] = None,
        append_tag: Optional[Tuple[str, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        append_response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        plugin_list: Optional[List[PluginParamType]] = None,
        append_plugin_list: Optional[List[PluginParamType]] = None,
    ) -> _PaitT:
        pre_depend_list = self._append_data(pre_depend_list, append_pre_depend_list, self._pre_depend_list)
        at_most_one_of_list = self._append_data(
            at_most_one_of_list, append_at_most_one_of_list, self._at_most_one_of_list
        )
        author = self._append_data(author, append_author, self._author)
        tag = self._append_data(tag, append_tag, self._tag)
        response_model_list = self._append_data(
            response_model_list, append_response_model_list, self._response_model_list
        )
        plugin_list = self._append_data(plugin_list, append_plugin_list, self._plugin_list)

        if append_required_by:
            required_by = (self._required_by or {}).update(append_required_by)
        else:
            required_by = required_by or self._required_by

        return self.__class__(
            make_mock_response_fn=make_mock_response_fn or self.make_mock_response_fn,
            enable_mock_response=enable_mock_response or self._enable_mock_response,
            pydantic_model_config=pydantic_model_config or self._pydantic_model_config,
            desc=desc or self._desc,
            summary=summary or self._summary,
            name=name or self._name,
            status=status or self._status,
            pre_depend_list=pre_depend_list,
            at_most_one_of_list=at_most_one_of_list,
            required_by=required_by,
            author=author,
            group=group,
            tag=tag,
            response_model_list=response_model_list,
            plugin_list=plugin_list,
        )

    @staticmethod
    def _plugin_handler(
        plugin_list: List[Tuple[Type[_PluginT], tuple, dict]],
        pait_core_model: PaitCoreModel,
        args: Any,
        kwargs: Any,
        func: Callable,
    ) -> List[_PluginT]:
        plugin_instance_list: List[_PluginT] = []
        for plugin_class, plugin_args, plugin_kwargs in plugin_list:
            plugin_instance: _PluginT = plugin_class(*plugin_args, **plugin_kwargs)
            plugin_instance.__post_init__(pait_core_model, args, kwargs)
            plugin_instance_list.append(plugin_instance)

        for index, plugin_instance in enumerate(plugin_instance_list):
            if plugin_instance == plugin_instance_list[-1]:
                setattr(plugin_instance, plugin_instance.call_next.__name__, func)
            else:
                setattr(plugin_instance, plugin_instance.call_next.__name__, plugin_instance_list[index + 1].__call__)
        return plugin_instance_list

    def __call__(
        self,
        make_mock_response_fn: Callable[[Type[PaitBaseResponseModel]], Any] = None,
        enable_mock_response: bool = False,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        append_pre_depend_list: Optional[List[Callable]] = None,
        at_most_one_of_list: Optional[List[List[str]]] = None,
        append_at_most_one_of_list: Optional[List[List[str]]] = None,
        required_by: Optional[Dict[str, List[str]]] = None,
        append_required_by: Optional[Dict[str, List[str]]] = None,
        # doc
        author: Optional[Tuple[str, ...]] = None,
        append_author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[TagT, ...]] = None,
        append_tag: Optional[Tuple[str, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        append_response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        plugin_list: Optional[List[PluginParamType]] = None,
        append_plugin_list: Optional[List[PluginParamType]] = None,
    ) -> Callable:
        app_name: str = self.app_helper_class.app_name
        enable_mock_response = enable_mock_response or self._enable_mock_response
        pydantic_model_config = pydantic_model_config or self._pydantic_model_config
        desc = desc or self._desc
        summary = summary or self._summary
        name = name or self._name
        group = group or self._group

        pre_depend_list = self._append_data(pre_depend_list, append_pre_depend_list, self._pre_depend_list)
        at_most_one_of_list = self._append_data(
            at_most_one_of_list, append_at_most_one_of_list, self._at_most_one_of_list
        )
        author = self._append_data(author, append_author, self._author)
        tag = self._append_data(tag, append_tag, self._tag)
        response_model_list = self._append_data(
            response_model_list, append_response_model_list, self._response_model_list
        )
        _plugin_list: List[PluginParamType] = (
            self._append_data(plugin_list, append_plugin_list, self._plugin_list) or []
        )
        if append_required_by:
            required_by = (self._required_by or {}).update(append_required_by)
        else:
            required_by = required_by or self._required_by

        ###############
        # tag handler #
        ###############
        new_tag: List[str] = []
        if tag:
            for _tag in tag:
                if isinstance(_tag, Tag):
                    _tag = _tag.name
                else:
                    logging.warning("In later versions tag only supports Tag class, and does not support str type")
                new_tag.append(_tag)

        def wrapper(func: Callable) -> Callable:
            # Pre-parsing function signatures
            get_func_sig(func)

            # gen pait core model and register to pait data
            pait_core_model: PaitCoreModel = PaitCoreModel(
                author=author,
                app_helper_class=self.app_helper_class,
                make_mock_response_fn=make_mock_response_fn or self._make_mock_response_fn,
                desc=desc,
                summary=summary,
                func=func,
                func_name=name,
                status=status,
                group=group,
                tag=tuple(new_tag),
                response_model_list=response_model_list,
                pre_depend_list=pre_depend_list,
                pydantic_model_config=pydantic_model_config,
                at_most_one_of_list=at_most_one_of_list,
                required_by=required_by,
            )
            sync_config_data_to_pait_core_model(config, pait_core_model, enable_mock_response=enable_mock_response)
            pait_data.register(app_name, pait_core_model)

            if inspect.iscoroutinefunction(func):
                for plugin, _, _ in _plugin_list:
                    if not issubclass(plugin, BaseAsyncPlugin):
                        raise TypeError("Plugin must BaseAsyncPlugin subclass")
                _plugin_list.append((AsyncParamHandler, (), {}))

                @wraps(func)
                async def dispatch(*args: Any, **kwargs: Any) -> Callable:
                    first_plugin: BaseAsyncPlugin = self._plugin_handler(  # type: ignore
                        _plugin_list, pait_core_model, args, kwargs, func
                    )[0]
                    return await first_plugin(*args, **kwargs)

                return dispatch
            else:
                for plugin, args, kwargs in _plugin_list:
                    if not issubclass(plugin, BasePlugin):
                        raise TypeError("Plugin must BasePlugin subclass")
                _plugin_list.append((ParamHandler, (), {}))

                @wraps(func)
                def dispatch(*args: Any, **kwargs: Any) -> Callable:
                    first_plugin: BasePlugin = self._plugin_handler(  # type: ignore
                        _plugin_list, pait_core_model, args, kwargs, func
                    )[0]
                    return first_plugin(*args, **kwargs)

                return dispatch

        return wrapper
