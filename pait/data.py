import logging
from types import CodeType
from typing import TYPE_CHECKING, Dict, Set

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class PaitData(object):
    def __init__(self) -> None:
        self.pait_id_dict: Dict[str, Dict[str, "PaitCoreModel"]] = {}

    def register(self, app_name: str, pait_info_model: "PaitCoreModel") -> None:
        """Store the data of each routing handle"""
        pait_id: str = pait_info_model.pait_id
        if app_name not in self.pait_id_dict:
            self.pait_id_dict[app_name] = {}
        self.pait_id_dict[app_name][pait_id] = pait_info_model

    def get_pait_data(self, app_name: str, pait_id: str) -> "PaitCoreModel":
        """Get route handle data"""
        return self.pait_id_dict[app_name][pait_id]

    def add_route_info(
        self,
        app_name: str,
        pait_id: str,
        path: str,
        openapi_path: str,
        method_set: Set[str],
        route_name: str,
        project_name: str,
    ) -> None:
        """Route handle information supplemented by load_app"""
        if pait_id in self.pait_id_dict[app_name]:
            model: "PaitCoreModel" = self.pait_id_dict[app_name][pait_id]
            model.path = path
            model.openapi_path = openapi_path
            model.method_list = sorted(list(method_set or set()), reverse=True)
            model.operation_id = route_name
            func_code: CodeType = model.func.__code__  # type: ignore
            if project_name:
                model.func_path = project_name + f"{project_name}".join(func_code.co_filename.split(project_name)[1:])
            else:
                model.func_path = func_code.co_filename
        else:
            logging.warning(f"load path:{path} fail, pait id:{pait_id}")

    def __bool__(self) -> bool:
        return bool(self.pait_id_dict)
