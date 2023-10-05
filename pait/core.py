import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from any_api.openapi.model.util import HttpMethodLiteral
from typing_extensions import Required, Self, TypedDict, Unpack, get_args

from pait.app.base import BaseAppHelper
from pait.exceptions import TipException
from pait.extra.util import sync_config_data_to_pait_core_model
from pait.g import config, pait_data, set_ctx
from pait.model.context import ContextModel
from pait.model.core import (
    AuthorOptionalType,
    DefaultFieldClassOptionalType,
    DefaultValue,
    DependListOptionalType,
    DescOptionalType,
    FuncNameOptionalType,
    GroupOptionalType,
    OperationIdOptionalType,
    OptionalBoolType,
    PaitCoreModel,
    PluginListOptionalType,
    PostPluginListOptionalType,
ExtraOpenAPIModelListOptionalType,
    ResponseModelListOptionalType,
    StatusOptionalType,
    SummaryOptionalType,
    TagOptionalType,
    get_core_model,
)
from pait.model.response import BaseResponseModel
from pait.param_handle import AsyncParamHandler, BaseParamHandler, ParamHandler
from pait.util import get_func_sig

_AppendT = TypeVar("_AppendT", list, tuple)


class PaitBaseParamTypedDict(TypedDict, total=False):
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
    :param extra_openapi_model_list: Supplement the OpenAPI data of routing functions,
        for example, when using a stream to upload file. If cannot use File(xxx) in a route and can only use the
        stream of the request object to obtain data, can supplement the OpenAPI information with extra_openapi_model_list
    :param response_model_list: The response object of the route function
    :param plugin_list: pre plugin for routing functions
    :param post_plugin_list: post plugin list for routing functions
    :param sync_to_thread: if True, use AsyncParamHandler and run sync func in asyncio.thread pool
    :param feature_code: Specify the prefix of the pait id corresponding to the generated routing function.
        Usually, the pait_id is equal to md5(func), but during dynamic generation,
        there may be multiple different routing functions generated by the same func.
        In this case, different feature_code is needed to generate different pait_id(feature_code + md5(func))
    :param auto_build:
        If true, then the plugin will be automatically built when the core model is generated.
        Otherwise, you need to manually call the core_model'build' method.
        If you are using a cbv route, recommend that set auto_build=False
    :param tip_exception_class: Tip Exception class
    :param extra: Extended parameters for plugins
    """

    default_field_class: DefaultFieldClassOptionalType
    pre_depend_list: DependListOptionalType
    # doc
    operation_id: OperationIdOptionalType
    author: AuthorOptionalType
    desc: DescOptionalType
    summary: SummaryOptionalType
    name: FuncNameOptionalType
    status: StatusOptionalType
    group: GroupOptionalType
    tag: TagOptionalType
    extra_openapi_model_list: ExtraOpenAPIModelListOptionalType
    response_model_list: ResponseModelListOptionalType
    # plugin
    plugin_list: PluginListOptionalType
    post_plugin_list: PostPluginListOptionalType
    sync_to_thread: OptionalBoolType
    # other
    feature_code: Optional[str]
    auto_build: bool
    tip_exception_class: Optional[Type[TipException]]
    extra: Dict


class PaitInitParamTypedDict(PaitBaseParamTypedDict, total=False):
    """
    :param param_handler_plugin: The param handler plugin of the routing function,
        the default is pait.param_handler.x
    """

    param_handler_plugin: Optional[Type[BaseParamHandler]]


class PaitCreateSubParamTypedDict(PaitInitParamTypedDict, total=False):
    """
    :param append_pre_depend_list: Append some author when creating child Pait
    :param append_author: Append some author when creating child Pait
    :param append_tag: Append some tags when creating child Pait
    :param append_extra_openapi_model_list: Append some extra openapi model object when creating child Pait
    :param append_response_model_list: Append some response object when creating child Pait
    :param append_plugin_list: Append some pre plugin when creating child Pait
    :param append_post_plugin_list:  Append some post plugin when creating child Pait
    """

    append_pre_depend_list: DependListOptionalType
    append_author: AuthorOptionalType
    append_tag: TagOptionalType
    append_extra_openapi_model_list: ExtraOpenAPIModelListOptionalType
    append_response_model_list: ResponseModelListOptionalType
    append_plugin_list: PluginListOptionalType
    append_post_plugin_list: PostPluginListOptionalType


class _PaitCoreModelTypedDict(PaitBaseParamTypedDict, total=False):
    param_handler_plugin: Required[Type[BaseParamHandler]]


base_param_key_list = list(PaitInitParamTypedDict.__annotations__.keys())
with_append_param_key_list = list(PaitCreateSubParamTypedDict.__annotations__.keys())
only_append_param_key_list = list(set(with_append_param_key_list) - set(base_param_key_list))
only_need_append_param_key_list = [i.replace("append_", "") for i in only_append_param_key_list]


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
    elif not target_container:
        return self_container
    else:
        return target_container


def easy_to_develop_merge_kwargs(
    before_param: Union[PaitInitParamTypedDict, PaitCreateSubParamTypedDict],
    after_param: Union[PaitInitParamTypedDict, PaitCreateSubParamTypedDict],
) -> PaitInitParamTypedDict:
    """
    A large number of similar parameters are used in the Pait project,
     but during development we don't want to write them all over again each time,
     so we solve this problem with Unpack[TypedDict].

    In practice, however, we may have some special needs, such as the handling of `append_xxx` and `extra` parameters,
     as well as the merging of parameters when calling, etc.
    This function exists to solve these problems, it may bring a little bit of performance loss,
     but provides very high development efficiency, while it will only be called once at initialization time,
     which has little impact.
    """
    # init extra key
    if "extra" not in after_param or not after_param["extra"]:
        after_param["extra"] = {}

    for key in PaitCreateSubParamTypedDict.__annotations__.keys():
        if key in only_need_append_param_key_list:
            # handler append param
            append_key = f"append_{key}"
            after_param[key] = _append_data(  # type: ignore[literal-required] # why mypy not support?
                key,
                after_param.get(key, None),
                after_param.get(append_key, None),
                before_param.get(key, None),
            )
            after_param.pop(append_key, None)  # type: ignore[misc]
        elif not (key in after_param and after_param[key] is not None) and key in before_param:  # type: ignore
            # merge data
            after_param[key] = before_param[key]  # type: ignore[literal-required] # mypy why not support?

    return after_param


class Pait(object):
    app_helper_class: "Type[BaseAppHelper]"
    param_handler_plugin_class: Type[ParamHandler] = ParamHandler
    async_param_handler_plugin_class: Type[AsyncParamHandler] = AsyncParamHandler

    def __init__(self, **kwargs: Unpack[PaitInitParamTypedDict]):
        """
        param doc see PaitInitParamTypedDict
        Can't do type hints and autocomplete? see: https://github.com/so1n/pait/issues/51
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
            raise TypeError(f"{self.app_helper_class} must sub from {getattr(BaseAppHelper.__class__, '__name__', '')}")

        if "extra" not in kwargs or not kwargs["extra"]:
            kwargs["extra"] = {}

        for key in list(kwargs.keys()):
            if key not in PaitCreateSubParamTypedDict.__annotations__:
                # Compatible with the extra parameter
                kwargs["extra"][key] = kwargs.pop(key, None)  # type: ignore[misc,literal-required]

        self._param_kwargs = kwargs
        if "auto_build" not in self._param_kwargs:
            self._param_kwargs["auto_build"] = True

    @staticmethod
    def init_context(pait_core_model: "PaitCoreModel", args: Any, kwargs: Any) -> ContextModel:
        """Inject App Helper into context"""
        app_helper: "BaseAppHelper" = pait_core_model.app_helper_class(args, kwargs)
        context: ContextModel = ContextModel(
            cbv_instance=app_helper.cbv_instance,
            app_helper=app_helper,
            pait_core_model=pait_core_model,
            args=args,
            kwargs=kwargs,
        )
        set_ctx(context)
        return context

    @property
    def param_kwargs(self) -> PaitInitParamTypedDict:
        return self._param_kwargs

    def create_sub_pait(self: Self, **kwargs: Unpack[PaitCreateSubParamTypedDict]) -> Self:
        """
        param doc see PaitCreateSubParamTypedDict
        Can't do type hints and autocomplete? see: https://github.com/so1n/pait/issues/51
        """
        return self.__class__(**easy_to_develop_merge_kwargs(self._param_kwargs, kwargs))

    @staticmethod
    def pre_load_cbv(cbv_class: Type, **kwargs: Unpack[PaitCreateSubParamTypedDict]) -> None:
        """
        This call allows you to fill in the new parameters and prepare the core model and its data
        for the CBV routing function in advance
        """
        for key in (
            "sync_to_thread",
            "feature_code",
            "plugin_list",
            "post_plugin_list",
            "param_handler_plugin",
            "name",
            "operation_id",
        ):
            if kwargs.get(key):
                raise ValueError(f"{key} can't be used in pre_load_cbv")

        append_pre_depend_list = kwargs.get("append_pre_depend_list", [])
        append_author = kwargs.get("append_author", tuple())
        append_tag = kwargs.get("append_tag", tuple())
        append_extra_openapi_model_list = kwargs.get("append_extra_openapi_model_list", [])
        append_response_model_list = kwargs.get("append_response_model_list", [])
        append_plugin_list = kwargs.get("append_plugin_list", [])
        append_post_plugin_list = kwargs.get("append_post_plugin_list", [])

        for http_method in get_args(HttpMethodLiteral):
            func = getattr(cbv_class, http_method, None)
            if not func:
                continue
            core_model = get_core_model(func)
            core_model.param_handler_plugin.check_cbv_handler(core_model, cbv_class)
            core_model.param_handler_plugin.add_cbv_prd(
                core_model, cbv_class, core_model.param_handler_pm.plugin_kwargs
            )
            if not core_model.default_field_class and kwargs.get("default_field_class"):
                core_model.default_field_class = kwargs.get("default_field_class")
            if not core_model.pre_depend_list and kwargs.get("pre_depend_list"):
                core_model.pre_depend_list = kwargs.get("pre_depend_list") or []
            if not core_model.author and kwargs.get("author"):
                core_model.author = kwargs.get("author") or tuple()
            if not core_model.desc and kwargs.get("desc"):
                core_model.desc = kwargs.get("desc") or ""
            if not core_model.summary and kwargs.get("summary"):
                core_model.summary = kwargs.get("summary") or ""
            if core_model.status is DefaultValue.status and kwargs.get("status"):
                core_model.status = kwargs.get("status") or DefaultValue.status
            if (not core_model.group or core_model.group is DefaultValue.group) and kwargs.get("group"):
                core_model.group = kwargs.get("group") or DefaultValue.group
            if (not core_model.tag or core_model.tag is DefaultValue.tag) and kwargs.get("tag"):
                core_model.tag = kwargs.get("tag") or DefaultValue.tag
            if not core_model.response_model_list and kwargs.get("response_model_list"):
                core_model.add_response_model_list(kwargs.get("response_model_list") or [])
            if not core_model.extra_openapi_model_list and kwargs.get("extra_openapi_model_list"):
                core_model.extra_openapi_model_list.extend(kwargs.get("extra_openapi_model_list") or [])
            if core_model.tip_exception_class is DefaultValue.tip_exception_class and kwargs.get("tip_exception_class"):
                core_model.tip_exception_class = kwargs.get("tip_exception_class")

            if append_pre_depend_list:
                core_model.pre_depend_list.extend(append_pre_depend_list)
            if append_author:
                if core_model.author:
                    core_model.author = core_model.author + append_author
                else:
                    core_model.author = append_author
            if append_tag:
                core_model.tag = core_model.tag + append_tag
            if append_extra_openapi_model_list:
                core_model.extra_openapi_model_list.extend(append_extra_openapi_model_list)
            if append_response_model_list:
                core_model.add_response_model_list(append_response_model_list)
            if append_plugin_list or append_post_plugin_list:
                core_model.add_plugin(append_plugin_list, append_post_plugin_list)

            core_model.build()

    def __call__(self, **kwargs: Unpack[PaitCreateSubParamTypedDict]) -> Callable:
        """
        param doc see PaitCallParamTypedDict
        Can't do type hints and autocomplete? see: https://github.com/so1n/pait/issues/51
        """
        app_name: str = self.app_helper_class.app_name
        merge_kwargs = easy_to_develop_merge_kwargs(self._param_kwargs, kwargs)
        sync_to_thread = merge_kwargs.get("sync_to_thread", False)

        def wrapper(func: Callable) -> Callable:
            # Pre-parsing function signatures
            get_func_sig(func)
            is_async_mode = inspect.iscoroutinefunction(func) or sync_to_thread

            # load param handler plugin
            _param_handler_plugin = merge_kwargs.pop("param_handler_plugin", None)
            if _param_handler_plugin is None:
                if is_async_mode:
                    _param_handler_plugin = self.async_param_handler_plugin_class
                else:
                    _param_handler_plugin = self.param_handler_plugin_class

            core_model_kwargs: _PaitCoreModelTypedDict = merge_kwargs  # type: ignore[assignment]
            core_model_kwargs["feature_code"] = kwargs.get("feature_code", "")
            core_model_kwargs["param_handler_plugin"] = _param_handler_plugin

            # gen pait core model and register to pait data
            pait_core_model = PaitCoreModel(func, self.app_helper_class, **core_model_kwargs)
            sync_config_data_to_pait_core_model(config, pait_core_model)
            pait_data.register(app_name, pait_core_model)
            if core_model_kwargs.get("auto_build", False):
                pait_core_model.build()

            if is_async_mode:

                @wraps(func)
                async def async_dispatch(*args: Any, **func_kwargs: Any) -> Callable:
                    context = self.init_context(pait_core_model, args, func_kwargs)
                    return await pait_core_model.main_plugin(context)

                return async_dispatch
            else:

                @wraps(func)
                def dispatch(*args: Any, **func_kwargs: Any) -> Callable:
                    context = self.init_context(pait_core_model, args, func_kwargs)
                    return pait_core_model.main_plugin(context)

                return dispatch

        return wrapper
