import inspect
import logging
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseConfig

from pait.app.base import BaseAppHelper
from pait.g import config, pait_data
from pait.model.core import PaitCoreModel
from pait.model.response import PaitBaseResponseModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag
from pait.model.util import sync_config_data_to_pait_core_model
from pait.plugin.base import BaseAsyncPlugin, BasePlugin, PluginManager
from pait.util import get_func_sig

_AppendT = TypeVar("_AppendT", list, tuple)
_PaitT = TypeVar("_PaitT", bound="Pait")
_PluginT = Union[BasePlugin, BaseAsyncPlugin]
TagT = Union[str, Tag]


class Pait(object):
    app_helper_class: "Type[BaseAppHelper]"

    def __init__(
        self,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        # doc
        author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[TagT, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        plugin_list: Optional[List[PluginManager]] = None,
        post_plugin_list: Optional[List[PluginManager]] = None,
    ):

        check_cls_param_list: List[str] = ["app_helper_class"]
        for cls_param in check_cls_param_list:
            if not getattr(self, cls_param, None):
                raise ValueError(
                    f"Please specify the value of the {cls_param} parameter, you can refer to `pait.app.xxx`"
                )
        if not isinstance(self.app_helper_class, type):
            raise TypeError(f"{self.app_helper_class} must be class")
        if not issubclass(self.app_helper_class, BaseAppHelper):
            raise TypeError(f"{self.app_helper_class} must sub from {BaseAppHelper.__class__.__name__}")

        self._pydantic_model_config: Optional[Type[BaseConfig]] = pydantic_model_config
        # param check
        self._pre_depend_list: Optional[List[Callable]] = pre_depend_list
        # doc
        self._author: Optional[Tuple[str, ...]] = author
        self._desc: Optional[str] = desc
        self._summary: Optional[str] = summary
        self._name: Optional[str] = name
        self._status: Optional[PaitStatus] = status
        self._group: Optional[str] = group
        self._tag: Optional[Tuple[TagT, ...]] = tag
        self._response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = response_model_list
        self._plugin_list: Optional[List[PluginManager]] = plugin_list
        self._post_plugin_list: Optional[List[PluginManager]] = post_plugin_list

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
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        append_pre_depend_list: Optional[List[Callable]] = None,
        # doc
        author: Optional[Tuple[str, ...]] = None,
        append_author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[TagT, ...]] = None,
        append_tag: Optional[Tuple[TagT, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        append_response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        plugin_list: Optional[List[PluginManager]] = None,
        append_plugin_list: Optional[List[PluginManager]] = None,
        post_plugin_list: Optional[List[PluginManager]] = None,
        append_post_plugin_list: Optional[List[PluginManager]] = None,
    ) -> _PaitT:
        pre_depend_list = self._append_data(pre_depend_list, append_pre_depend_list, self._pre_depend_list)
        author = self._append_data(author, append_author, self._author)
        tag = self._append_data(tag, append_tag, self._tag)
        response_model_list = self._append_data(
            response_model_list, append_response_model_list, self._response_model_list
        )
        plugin_list = self._append_data(plugin_list, append_plugin_list, self._plugin_list)
        post_plugin_list = self._append_data(post_plugin_list, append_post_plugin_list, self._post_plugin_list)

        return self.__class__(
            pydantic_model_config=pydantic_model_config or self._pydantic_model_config,
            desc=desc or self._desc,
            summary=summary or self._summary,
            name=name or self._name,
            status=status or self._status,
            pre_depend_list=pre_depend_list,
            author=author,
            group=group,
            tag=tag,
            response_model_list=response_model_list,
            plugin_list=plugin_list,
            post_plugin_list=post_plugin_list,
        )

    @staticmethod
    def _plugin_manager_handler(
        pait_core_model: PaitCoreModel,
        args: Any,
        kwargs: Any,
        func: Callable,
    ) -> List[_PluginT]:
        plugin_instance_list: List[_PluginT] = []

        pre_plugin: Callable = func
        for plugin_manager in pait_core_model.plugin_list:
            plugin_instance: _PluginT = plugin_manager.get_plugin()
            plugin_instance.__post_init__(pait_core_model, args, kwargs)
            plugin_instance.call_next = pre_plugin  # type: ignore
            pre_plugin = plugin_instance
            plugin_instance_list.append(plugin_instance)
        plugin_instance_list.reverse()
        return plugin_instance_list

    def __call__(
        self,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        append_pre_depend_list: Optional[List[Callable]] = None,
        # doc
        author: Optional[Tuple[str, ...]] = None,
        append_author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[TagT, ...]] = None,
        append_tag: Optional[Tuple[TagT, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        append_response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        plugin_list: Optional[List[PluginManager]] = None,
        append_plugin_list: Optional[List[PluginManager]] = None,
        post_plugin_list: Optional[List[PluginManager]] = None,
        append_post_plugin_list: Optional[List[PluginManager]] = None,
    ) -> Callable:
        app_name: str = self.app_helper_class.app_name
        pydantic_model_config = pydantic_model_config or self._pydantic_model_config
        desc = desc or self._desc
        summary = summary or self._summary
        name = name or self._name
        group = group or self._group

        pre_depend_list = self._append_data(pre_depend_list, append_pre_depend_list, self._pre_depend_list)
        author = self._append_data(author, append_author, self._author)
        tag = self._append_data(tag, append_tag, self._tag)
        response_model_list = self._append_data(
            response_model_list, append_response_model_list, self._response_model_list
        )
        plugin_list = self._append_data(plugin_list, append_plugin_list, self._plugin_list)
        post_plugin_list = self._append_data(post_plugin_list, append_post_plugin_list, self._post_plugin_list)

        ###############
        # tag handler #
        ###############
        new_tag: List[str] = []
        if tag:
            for _tag in tag:
                if isinstance(_tag, Tag):
                    _tag = _tag.name
                else:
                    logging.warning(
                        "In later versions tag only supports Tag class, and does not support str type"
                    )  # pragma: no cover
                new_tag.append(_tag)

        def wrapper(func: Callable) -> Callable:
            # Pre-parsing function signatures
            get_func_sig(func)
            # gen pait core model and register to pait data
            pait_core_model: PaitCoreModel = PaitCoreModel(
                author=author,
                app_helper_class=self.app_helper_class,
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
                plugin_list=plugin_list,
                post_plugin_list=post_plugin_list,
            )
            sync_config_data_to_pait_core_model(config, pait_core_model)
            pait_data.register(app_name, pait_core_model)
            if inspect.iscoroutinefunction(func):

                @wraps(func)
                async def dispatch(*args: Any, **kwargs: Any) -> Callable:
                    first_plugin: BaseAsyncPlugin = self._plugin_manager_handler(  # type: ignore
                        pait_core_model, args, kwargs, func
                    )[0]
                    return await first_plugin(*args, **kwargs)

                return dispatch
            else:

                @wraps(func)
                def dispatch(*args: Any, **kwargs: Any) -> Callable:
                    first_plugin: BasePlugin = self._plugin_manager_handler(  # type: ignore
                        pait_core_model, args, kwargs, func
                    )[0]
                    return first_plugin(*args, **kwargs)

                return dispatch

        return wrapper
