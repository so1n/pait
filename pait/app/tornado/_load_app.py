import logging
from typing import Callable, Dict, Optional

from tornado.web import Application, RequestHandler

from pait.data import PaitCoreProxyModel
from pait.g import pait_data
from pait.model.core import PaitCoreModel

from ._app_helper import AppHelper
from ._pait import Pait
from ._pait import pait as default_pait

__all__ = ["load_app", "get_openapi_path"]


def get_openapi_path(path: str) -> str:
    openapi_path: str = path
    # replace path regex to {xxx}
    if "<" in openapi_path and ">" in openapi_path:
        new_path_list: list = []
        for sub_path in openapi_path.split("/"):
            if not sub_path:
                continue

            l_index: int = sub_path.find("<")
            r_index: int = sub_path.find(">")
            if l_index != -1 and r_index != -1:
                real_sub_path = "{" + sub_path[l_index + 1 : r_index] + "}"
            else:
                real_sub_path = sub_path
            new_path_list.append(real_sub_path)
        openapi_path = "/".join(new_path_list)
    if not openapi_path.startswith("/"):
        openapi_path = "/" + openapi_path
    return openapi_path


def load_app(
    app: Application,
    auto_load_route: bool = False,
    override_operation_id: bool = False,
    overwrite_already_exists_data: bool = False,
    pait: Pait = default_pait,
    auto_cbv_handle: bool = True,
) -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for rule in app.wildcard_router.rules:
        path: str = rule.matcher.regex.pattern  # type: ignore
        if path.endswith("$"):
            path = path[:-1]
        openapi_path = get_openapi_path(path)

        base_name: str = rule.target.__name__
        for method in ["get", "post", "head", "options", "delete", "put", "trace", "patch"]:
            handler: Optional[Callable] = getattr(rule.target, method, None)
            if not handler:
                continue
            if handler is RequestHandler._unimplemented_method:
                continue
            route_name: str = f"{base_name}.{method}"
            pait_id: str = getattr(handler, "_pait_id", "")
            if not pait_id:
                if auto_load_route:

                    handler = pait()(handler)
                    pait_id = getattr(handler, "_pait_id")
                    setattr(rule.target, method, handler)
                else:
                    logging.warning(f"{route_name} can not found pait id")  # pragma: no cover
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
                if auto_cbv_handle:
                    real_core_model = PaitCoreProxyModel.get_core_model(core_model)
                    real_core_model.param_handler_plugin.check_cbv_handler(real_core_model, rule.target)
                    real_core_model.param_handler_plugin.add_cbv_prd(
                        real_core_model, rule.target, real_core_model.param_handler_pm.plugin_kwargs
                    )
                    real_core_model.build()
                _pait_data[pait_id] = core_model
    return _pait_data
