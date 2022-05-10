from dataclasses import MISSING
from importlib import import_module
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type

from pydantic import BaseConfig

from pait.core import PluginManager, TagT
from pait.model.status import PaitStatus

from ..model.core import PaitCoreModel  # type: ignore
from ..model.response import PaitBaseResponseModel  # type: ignore
from .auto_load_app import auto_load_app_class  # type: ignore
from .base.util import sniffing

if TYPE_CHECKING:
    from pait.param_handle import BaseParamHandler

try:
    load_class_app: Any = auto_load_app_class()
    pait_app_path: str = "pait.app." + load_class_app.__name__.lower()
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
        from pait.app.base.grpc_route import GrpcGatewayRoute as _GrpcGatewayRoute
        from pait.core import Pait as _Pait

    Pait: "_Pait" = getattr(import_module(pait_app_path), "Pait")
    AddDocRoute: "_AddDocRoute" = getattr(import_module(pait_app_path), "AddDocRoute")
    GrpcGatewayRoute: "_GrpcGatewayRoute" = getattr(import_module(pait_app_path + ".grpc_route"), "GrpcGatewayRoute")
except RuntimeError:  # pragma: no cover
    # Automatic loading of classes, loading failure when the user can not use
    pait_app_path = ""  # pragma: no cover


def _import_func_from_app(app: Any, fun_name: str) -> Callable:
    app_name: str = sniffing(app)
    return getattr(import_module(f"pait.app.{app_name}"), fun_name)


def _base_call_func(app: Any, fun_name: str, *args: Any, **kwargs: Any) -> Any:
    return _import_func_from_app(app, fun_name)(*args, **kwargs)


def load_app(app: Any, project_name: str = "") -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`
    Note:This is an implicit method
    """
    return _base_call_func(app, "load_app", app, project_name=project_name)


def add_doc_route(
    app: Any,
    scheme: Optional[str] = None,
    open_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
    project_name: str = "",
) -> None:
    return _base_call_func(
        app,
        "add_doc_route",
        scheme=scheme,
        open_json_url_only_path=open_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        open_api_tag_list=open_api_tag_list,
        project_name=project_name,
    )


def pait(
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
    append_tag: Optional[Tuple[str, ...]] = None,
    response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
    append_response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
    plugin_list: Optional[List[PluginManager]] = None,
    append_plugin_list: Optional[List[PluginManager]] = None,
    param_handler_plugin: Optional[Type["BaseParamHandler"]] = None,
    feature_code: str = "",
) -> Callable:
    """provide parameter checks and type conversions for each routing function/cbv class
    Note:This is an implicit method
    """
    if not pait_app_path:
        raise RuntimeError("Auto load app fail")  # pragma: no cover
    _pait: Optional[Callable] = getattr(import_module(pait_app_path), "pait")
    if not _pait:
        raise NotImplementedError(f"Pait not support:{load_class_app}")
    return _pait(
        pydantic_model_config=pydantic_model_config,
        pre_depend_list=pre_depend_list,
        append_pre_depend_list=append_pre_depend_list,
        author=author,
        append_author=append_author,
        desc=desc,
        summary=summary,
        name=name,
        status=status,
        group=group,
        tag=tag,
        append_tag=append_tag,
        response_model_list=response_model_list,
        append_response_model_list=append_response_model_list,
        plugin_list=plugin_list,
        append_plugin_list=append_plugin_list,
        param_handler_plugin=param_handler_plugin,
        feature_code=feature_code,
    )


def set_app_attribute(app: Any, key: str, value: Any) -> None:
    app_name: str = sniffing(app)
    if app_name == "flask":
        app.config[key] = value
        from flask import g

        def _before_request() -> None:
            setattr(g, key, value)

        app.before_request(_before_request)
    elif app_name == "sanic":
        setattr(app.ctx, key, value)
    elif app_name == "starlette":
        setattr(app.state, key, value)
    elif app_name == "tornado":
        app.settings[key] = value


def get_app_attribute(app: Any, key: str) -> Any:
    app_name: str = sniffing(app)
    if app_name == "flask":
        value: Any = app.config.get(key, MISSING)
        if value is not MISSING:
            return value

        from flask import g

        return getattr(g, key)
    elif app_name == "starlette":
        return getattr(app.state, key)
    elif app_name == "sanic":
        return getattr(app.ctx, key)
    elif app_name == "tornado":
        return app.settings[key]
