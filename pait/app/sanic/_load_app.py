import logging
from typing import Callable, Dict, Optional, Set, Type

from sanic.app import Sanic
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.g import pait_data
from pait.model.core import PaitCoreModel

from ._app_helper import AppHelper

__all__ = ["load_app"]


def load_app(app: Sanic, project_name: str = "") -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for route in app.router.routes:
        if "static" in route.name:
            continue

        route_name: str = route.name
        method_set: Set[str] = route.methods
        path: str = route.path
        openapi_path: str = path
        handler: Callable = route.handler

        # replace path <xxx> to {xxx}
        if "<" in openapi_path and ">" in openapi_path:
            new_path_list: list = []
            for sub_path in openapi_path.split("/"):
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
        for method in method_set:
            view_class: Optional[Type] = getattr(handler, "view_class", None)
            if view_class:
                handler = getattr(view_class, method.lower(), None)
            if not handler:
                logging.warning(f"{route_name} can not found handle")
                continue
            pait_id: Optional[str] = getattr(handler, "_pait_id", None)
            if not pait_id:
                logging.warning(f"{route_name} can not found pait id")
                continue
            pait_data.add_route_info(
                AppHelper.app_name, pait_id, path, openapi_path, {method}, route_name, project_name
            )
            _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)

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
