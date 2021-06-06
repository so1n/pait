import logging
from typing import Any, Callable, Dict, Set

from pait.model import PaitCoreModel


class PaitData(object):
    def __init__(self) -> None:
        self.pait_id_dict: Dict[str, Dict[str, "PaitCoreModel"]] = {}

    def register(self, app_name: str, pait_info_model: "PaitCoreModel") -> None:
        pait_id: str = pait_info_model.pait_id
        if app_name not in self.pait_id_dict:
            self.pait_id_dict[app_name] = {}
        self.pait_id_dict[app_name][pait_id] = pait_info_model

    def get_pait_data(self, app_name: str, pait_id: str) -> PaitCoreModel:
        return self.pait_id_dict[app_name][pait_id]

    def add_route_info(
        self, app_name: str, pait_id: str, path: str, method_set: Set[str], route_name: str, project_name: str
    ) -> None:
        if pait_id in self.pait_id_dict[app_name]:
            model: PaitCoreModel = self.pait_id_dict[app_name][pait_id]
            model.path = path
            model.method_list = sorted(list(method_set or set()), reverse=True)
            model.operation_id = route_name
            if project_name:
                model.func_path = project_name + f"{project_name}".join(
                    model.func.__code__.co_filename.split(project_name)[1:]
                )
            else:
                model.func_path = model.func.__code__.co_filename
        else:
            logging.warning(f"loan path:{path} fail, pait id:{pait_id}")

    #
    # def __getitem__(self, item: Any) -> Any:
    #     return self.pait_id_dict[item]
    #
    # def __setitem__(self, key: str, value: "PaitCoreModel") -> None:
    #     self.pait_id_dict[key] = value

    def __bool__(self) -> bool:
        return bool(self.pait_id_dict)
