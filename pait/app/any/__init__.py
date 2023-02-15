from dataclasses import MISSING
from importlib import import_module
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type

from pydantic import BaseConfig, BaseModel

from pait.app.any.util import base_call_func, sniffing
from pait.app.auto_load_app import auto_load_app_class
from pait.model.core import PaitCoreModel
from pait.model.response import BaseResponseModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag
from pait.plugin.base import PluginManager, PostPluginProtocol, PrePluginProtocol

if TYPE_CHECKING:
    from pait.app.base.simple_route import SimpleRoute
    from pait.openapi.openapi import OpenAPI
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
except RuntimeError:  # pragma: no cover
    # Automatic loading of classes, loading failure when the user can not use
    pait_app_path = ""  # pragma: no cover


def load_app(app: Any, project_name: str = "", auto_load_route: bool = False) -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`
    Note:This is an implicit method
    """
    return base_call_func("load_app", app, project_name=project_name, app=app, auto_load_route=auto_load_route)


def add_doc_route(
    app: Any,
    scheme: Optional[str] = None,
    openapi_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    openapi: Optional[Type["OpenAPI"]] = None,
    project_name: str = "",
) -> None:
    return base_call_func(
        "add_doc_route",
        app,
        app=app,
        scheme=scheme,
        openapi_json_url_only_path=openapi_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        openapi=openapi,
        project_name=project_name,
    )


def pait(
    pydantic_model_config: Optional[Type[BaseConfig]] = None,
    pydantic_basemodel: Optional[Type[BaseModel]] = None,
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
    """provide parameter checks and type conversions for each routing function/cbv class
    Note:This is an implicit method
    """
    if not pait_app_path:
        raise RuntimeError("Auto load app fail")  # pragma: no cover
    _pait: Optional[Callable] = getattr(import_module(pait_app_path), "pait")
    if not _pait:
        raise NotImplementedError(f"Pait not support:{load_class_app}")
    return _pait(
        pydantic_basemodel=pydantic_basemodel,
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
        post_plugin_list=post_plugin_list,
        append_post_plugin_list=append_post_plugin_list,
        param_handler_plugin=param_handler_plugin,
        feature_code=feature_code,
        **kwargs,
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


def add_simple_route(
    app: Any,
    simple_route: "SimpleRoute",
) -> None:
    base_call_func("add_simple_route", app, simple_route, app=app)


def add_multi_simple_route(
    app: Any, *simple_route_list: "SimpleRoute", prefix: str = "/", title: str = "", **kwargs: Any
) -> None:
    base_call_func("add_multi_simple_route", app, *simple_route_list, app=app, prefix=prefix, title=title, **kwargs)
