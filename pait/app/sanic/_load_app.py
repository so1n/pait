import logging
from typing import Callable, Dict, Optional, Set, Type

from sanic.app import Sanic

from pait.data import PaitCoreProxyModel
from pait.g import pait_data
from pait.model.core import PaitCoreModel

from ._app_helper import AppHelper
from ._pait import Pait
from ._pait import pait as default_pait

__all__ = ["load_app", "get_openapi_path"]


def get_openapi_path(path: str) -> str:
    openapi_path: str = path
    if "<" in openapi_path and ">" in openapi_path:
        new_path_list: list = []
        for sub_path in openapi_path.split("/"):
            if not sub_path:
                continue
            if sub_path[0] == "<" and sub_path[-1] == ">":
                real_sub_path: str = sub_path[1:-1]
                if ":" in real_sub_path:
                    real_sub_path = real_sub_path.split(":")[0]
                real_sub_path = "{" + real_sub_path + "}"
            else:
                real_sub_path = sub_path
            new_path_list.append(real_sub_path)
        openapi_path = "/".join(new_path_list)
    if not openapi_path.startswith("/"):
        openapi_path = "/" + openapi_path
    return openapi_path


def load_app(
    app: Sanic,
    auto_load_route: bool = False,
    override_operation_id: bool = False,
    overwrite_already_exists_data: bool = False,
    pait: Pait = default_pait,
    auto_cbv_handle: bool = True,
) -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for route in app.router.routes:
        route_name: str = route.name
        method_set: Set[str] = route.methods or set()
        path: str = route.path
        if not path.startswith("/"):
            path = "/" + path
        openapi_path = get_openapi_path(path)
        handler: Callable = route.handler

        for method in method_set:
            view_class: Optional[Type] = getattr(handler, "view_class", None)
            if view_class:
                real_handler: Optional[Callable] = getattr(view_class, method.lower(), None)
            else:
                real_handler = handler
            if not real_handler:
                logging.warning(f"{route_name} can not found handle")  # pragma: no cover
                continue
            pait_id: str = getattr(real_handler, "_pait_id", "")
            if not pait_id:
                if auto_load_route:
                    real_handler = pait()(real_handler)
                    pait_id = getattr(real_handler, "_pait_id", "")

                    if view_class:
                        setattr(view_class, method.lower(), real_handler)
                    else:
                        route.handler = real_handler
                else:
                    logging.warning(f"{route_name} can not found pait id")  # pragma: no cover
                    continue

            core_model = pait_data.get_core_model(
                AppHelper.app_name,
                pait_id,
                path,
                openapi_path,
                {method},
                route_name if override_operation_id else "",
                overwrite_already_exists_data=overwrite_already_exists_data,
            )
            if core_model:
                if view_class:
                    if auto_cbv_handle:
                        real_core_model = PaitCoreProxyModel.get_core_model(core_model)
                        real_core_model.param_handler_plugin.check_cbv_handler(real_core_model, view_class)
                        real_core_model.param_handler_plugin.add_cbv_prd(
                            real_core_model, view_class, real_core_model.param_handler_pm.plugin_kwargs
                        )
                        real_core_model.build()
                _pait_data[pait_id] = core_model

        # old version
        # for path, handler_dict in route.handlers.items():
        #     for method, handler_list in handler_dict.items():
        #         for handler in handler_list:
        #             view_class: Optional[Type] = getattr(handler, "view_class", None)
        #             if view_class:
        #                 handler = getattr(view_class, method.lower(), None)
        #             if not handler:
        #                 logging.warning(f"{route_name} can not found handle")
        #                 continue
        #             pait_id: Optional[str] = getattr(handler, "_pait_id", None)
        #             if not pait_id:
        #                 logging.warning(f"{route_name} can not found pait id")
        #                 continue
        #             pait_data.add_route_info(AppHelper.app_name, pait_id, path, {method}, route_name, project_name)
        #             _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data
