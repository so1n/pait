import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple, Type, TypeVar

from pait.app.base import BaseAppHelper
from pait.extra.util import sync_config_data_to_pait_core_model
from pait.field import BaseRequestResourceField
from pait.g import config, pait_context, pait_data
from pait.model.context import ContextModel
from pait.model.core import PaitCoreModel
from pait.model.response import BaseResponseModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag
from pait.param_handle import AsyncParamHandler, ParamHandler
from pait.plugin.base import PluginManager, PluginProtocol, PostPluginProtocol, PrePluginProtocol
from pait.util import get_func_sig

if TYPE_CHECKING:
    from param_handle import BaseParamHandler
_AppendT = TypeVar("_AppendT", list, tuple)
_PaitT = TypeVar("_PaitT", bound="Pait")
_PluginT = TypeVar("_PluginT", bound="PluginProtocol")


class Pait(object):
    app_helper_class: "Type[BaseAppHelper]"
    param_handler_plugin_class: Type[ParamHandler] = ParamHandler
    async_param_handler_plugin_class: Type[AsyncParamHandler] = AsyncParamHandler

    def __init__(
        self: "_PaitT",
        default_field_class: Optional[Type[BaseRequestResourceField]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        # doc
        operation_id: Optional[str] = None,
        author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[Tag, ...]] = None,
        response_model_list: Optional[List[Type[BaseResponseModel]]] = None,
        # plugin
        plugin_list: Optional[List[PluginManager[PrePluginProtocol]]] = None,
        post_plugin_list: Optional[List[PluginManager[PostPluginProtocol]]] = None,
        param_handler_plugin: Optional[Type["BaseParamHandler"]] = None,
        **kwargs: Any,
    ):
        """
        :param default_field_class: pait.field.BaseRequestResourceField
        :param pre_depend_list:  List of depend functions to execute before route functions
        :param operation_id: The unique identifier of the routing function
        :param author:  The author who wrote this routing function
        :param desc:  Description of the routing function
        :param summary:  Introduction to Routing Functions
        :param name:  The name of the routing function, defaults to the function name
        :param status:  The state of the routing function
        :param group:  The group to which the routing function belongs
        :param tag:  A collection of labels for routing functions
        :param response_model_list: The response object of the route function
        :param plugin_list: pre plugin for routing functions
        :param post_plugin_list: post plugin list for routing functions
        :param param_handler_plugin: The param handler plugin of the routing function,
            the default is pait.param_handler.x
        """

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

        self._default_field_class: Optional[Type[BaseRequestResourceField]] = default_field_class
        # param check
        self._pre_depend_list: Optional[List[Callable]] = pre_depend_list
        # doc
        self._operation_id: Optional[str] = operation_id
        self._author: Optional[Tuple[str, ...]] = author
        self._desc: Optional[str] = desc
        self._summary: Optional[str] = summary
        self._name: Optional[str] = name
        self._status: Optional[PaitStatus] = status
        self._group: Optional[str] = group
        self._tag: Optional[Tuple[Tag, ...]] = tag
        self._response_model_list: Optional[List[Type[BaseResponseModel]]] = response_model_list
        # plugin
        self._plugin_list: Optional[List[PluginManager[PrePluginProtocol]]] = plugin_list
        self._post_plugin_list: Optional[List[PluginManager[PostPluginProtocol]]] = post_plugin_list
        self._param_handler_plugin: Optional[Type["BaseParamHandler"]] = param_handler_plugin
        self.extra: dict = kwargs

    @staticmethod
    def _append_data(
        key: str,
        target_container: Optional[_AppendT],
        append_container: Optional[_AppendT],
        self_container: Optional[_AppendT],
    ) -> Optional[_AppendT]:
        if target_container and append_container:
            raise KeyError(f"{key} and append_{key} cannot be used together")  # pragma: no cover
        if append_container:
            return (self_container or append_container.__class__()) + append_container
        elif target_container is None:
            return self_container
        else:
            return target_container

    @property
    def response_model_list(self) -> List[Type[BaseResponseModel]]:
        return self._response_model_list or []

    def create_sub_pait(
        self: "_PaitT",
        default_field_class: Optional[Type[BaseRequestResourceField]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        append_pre_depend_list: Optional[List[Callable]] = None,
        # doc
        operation_id: Optional[str] = None,
        author: Optional[Tuple[str, ...]] = None,
        append_author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[Tag, ...]] = None,
        append_tag: Optional[Tuple[Tag, ...]] = None,
        response_model_list: Optional[List[Type[BaseResponseModel]]] = None,
        append_response_model_list: Optional[List[Type[BaseResponseModel]]] = None,
        plugin_list: Optional[List[PluginManager[PrePluginProtocol]]] = None,
        append_plugin_list: Optional[List[PluginManager[PrePluginProtocol]]] = None,
        post_plugin_list: Optional[List[PluginManager[PostPluginProtocol]]] = None,
        append_post_plugin_list: Optional[List[PluginManager[PostPluginProtocol]]] = None,
        param_handler_plugin: Optional[Type["BaseParamHandler"]] = None,
        **kwargs: Any,
    ) -> _PaitT:
        """
        :param default_field_class: pait.field.BaseRequestResourceField
        :param pre_depend_list:  List of depend functions to execute before route functions(
            Do not use the pre depend value specified when Pait is initialized)
        :param append_pre_depend_list: Append some author when creating child Pait
        :param operation_id: The unique identifier of the routing function
        :param author:  The author who wrote this routing function(
            Do not use the author value specified when Pait is initialized)
        :param append_author: Append some author when creating child Pait
        :param desc:  Description of the routing function
        :param summary:  Introduction to Routing Functions
        :param name:  The name of the routing function, defaults to the function name
        :param status:  The state of the routing function
        :param group:  The group to which the routing function belongs
        :param tag:  A collection of labels for routing functions(
            Do not use the tag value specified when Pait is initialized)
        :param append_tag: Append some tags when creating child Pait
        :param response_model_list: The response object of the route function(
            Do not use the response model value specified when Pait is initialized)
        :param append_response_model_list: Append some response object when creating child Pait
        :param plugin_list: pre plugin for routing functions(
            Do not use the pre plugin value specified when Pait is initialized)
        :param append_plugin_list: Append some pre plugin when creating child Pait
        :param post_plugin_list: post plugin list for routing functions(
            Do not use the post plugin value specified when Pait is initialized)
        :param append_post_plugin_list:  Append some post plugin when creating child Pait
        :param param_handler_plugin: The param handler plugin of the routing function,
         the default is pait.param_handler.x
        """
        pre_depend_list = self._append_data(
            "pre_depend_list", pre_depend_list, append_pre_depend_list, self._pre_depend_list
        )
        author = self._append_data("author", author, append_author, self._author)
        tag = self._append_data("tag", tag, append_tag, self._tag)
        response_model_list = self._append_data(
            "response_model_list", response_model_list, append_response_model_list, self._response_model_list
        )
        plugin_list = self._append_data("plugin_list", plugin_list, append_plugin_list, self._plugin_list)
        post_plugin_list = self._append_data(
            "post_plugin_list", post_plugin_list, append_post_plugin_list, self._post_plugin_list
        )

        return self.__class__(
            default_field_class=default_field_class or self._default_field_class,
            operation_id=operation_id,
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
            param_handler_plugin=param_handler_plugin or self._param_handler_plugin,
            **(kwargs or self.extra),
        )

    @staticmethod
    def init_context(pait_core_model: "PaitCoreModel", args: Any, kwargs: Any) -> ContextModel:
        """Inject App Helper into context"""
        app_helper: BaseAppHelper = pait_core_model.app_helper_class(args, kwargs)
        context: ContextModel = ContextModel(
            cbv_instance=app_helper.cbv_instance,
            app_helper=app_helper,
            pait_core_model=pait_core_model,
            args=args,
            kwargs=kwargs,
        )
        pait_context.set(context)
        return context

    def __call__(
        self: "_PaitT",
        default_field_class: Optional[Type[BaseRequestResourceField]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        append_pre_depend_list: Optional[List[Callable]] = None,
        # doc
        operation_id: Optional[str] = None,
        author: Optional[Tuple[str, ...]] = None,
        append_author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[Tag, ...]] = None,
        append_tag: Optional[Tuple[Tag, ...]] = None,
        response_model_list: Optional[List[Type[BaseResponseModel]]] = None,
        append_response_model_list: Optional[List[Type[BaseResponseModel]]] = None,
        # plugin
        plugin_list: Optional[List[PluginManager[PrePluginProtocol]]] = None,
        append_plugin_list: Optional[List[PluginManager[PrePluginProtocol]]] = None,
        post_plugin_list: Optional[List[PluginManager[PostPluginProtocol]]] = None,
        append_post_plugin_list: Optional[List[PluginManager[PostPluginProtocol]]] = None,
        param_handler_plugin: Optional[Type["BaseParamHandler"]] = None,
        feature_code: str = "",
        **kwargs: Any,
    ) -> Callable:
        """
        :param default_field_class: pait.field.BaseRequestResourceField
        :param pre_depend_list:  List of depend functions to execute before route functions
        :param operation_id: The unique identifier of the routing function
        :param author:  The author who wrote this routing function
        :param desc:  Description of the routing function
        :param summary:  Introduction to Routing Functions
        :param name:  The name of the routing function, defaults to the function name
        :param status:  The state of the routing function
        :param group:  The group to which the routing function belongs
        :param tag:  A collection of labels for routing functions(
            Do not use the tag value specified when Pait is initialized)
        :param append_tag: Append some tags to the routing function
        :param response_model_list: The response object of the route function(
            Do not use the response_model_list value specified when Pait is initialized)
        :param append_response_model_list: Append some response object to the routing function
        :param plugin_list: pre plugin for routing functions
        :param append_plugin_list: Append some pre plugin to the routing function (
            Do not use the pre plugin value specified when Pait is initialized)
        :param post_plugin_list: post plugin list for routing functions
        :param append_post_plugin_list:  Append some post plugin  to the routing function (
            Do not use the post plugin value specified when Pait is initialized)
        :param param_handler_plugin: The param handler plugin of the routing function,
            the default is pait.param_handler.x
        :param feature_code: Specify the prefix of the pait id corresponding to the generated routing function.
            Usually, the pait_id is equal to md5(func), but during dynamic generation,
            there may be multiple different routing functions generated by the same func.
            In this case, different feature_code is needed to generate different pait_id(feature_code + md5(func))
        """
        app_name: str = self.app_helper_class.app_name

        pre_depend_list = self._append_data(
            "pre_depend_list", pre_depend_list, append_pre_depend_list, self._pre_depend_list
        )
        author = self._append_data("author", author, append_author, self._author)
        tag = self._append_data("tag", tag, append_tag, self._tag)
        response_model_list = self._append_data(
            "response_model_list", response_model_list, append_response_model_list, self._response_model_list
        )
        plugin_list = self._append_data("plugin_list", plugin_list, append_plugin_list, self._plugin_list)
        post_plugin_list = self._append_data(
            "post_plugin_list", post_plugin_list, append_post_plugin_list, self._post_plugin_list
        )

        def wrapper(func: Callable) -> Callable:
            # Pre-parsing function signatures
            get_func_sig(func)

            # load param handler plugin
            _param_handler_plugin = param_handler_plugin or self._param_handler_plugin
            if _param_handler_plugin is None:
                if inspect.iscoroutinefunction(func):
                    _param_handler_plugin = self.async_param_handler_plugin_class
                else:
                    _param_handler_plugin = self.param_handler_plugin_class
            # gen pait core model and register to pait data
            pait_core_model: PaitCoreModel = PaitCoreModel(
                func,
                self.app_helper_class,
                operation_id=operation_id or self._operation_id,
                author=author,
                desc=desc or self._desc,
                summary=summary or self._summary,
                func_name=name or self._name,
                status=status or self._status,
                group=group or self._group,
                tag=tag,
                response_model_list=response_model_list,
                pre_depend_list=pre_depend_list,
                plugin_list=plugin_list,
                post_plugin_list=post_plugin_list,
                param_handler_plugin=_param_handler_plugin,
                feature_code=feature_code,
                default_field_class=default_field_class or self._default_field_class,
                **(kwargs or self.extra),
            )
            sync_config_data_to_pait_core_model(config, pait_core_model)
            pait_data.register(app_name, pait_core_model)
            if inspect.iscoroutinefunction(func):

                @wraps(func)
                async def dispatch(*args: Any, **kwargs: Any) -> Callable:
                    context: ContextModel = self.init_context(pait_core_model, args, kwargs)
                    return await pait_core_model.main_plugin(context)

                return dispatch
            else:

                @wraps(func)
                def dispatch(*args: Any, **kwargs: Any) -> Callable:
                    context = self.init_context(pait_core_model, args, kwargs)
                    return pait_core_model.main_plugin(context)

                return dispatch

        return wrapper
