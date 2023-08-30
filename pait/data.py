import copy
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Union

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class PaitCoreProxyModel(object):
    _self_key_list = ["_core_model", "operation_id"]
    _not_copy_key_list = ["func"]

    def __init__(self, core_model: "PaitCoreModel", operation_id: str) -> None:
        self._core_model = core_model
        self.operation_id = operation_id

    def __getattr__(self, key: Any) -> None:
        try:
            return super().__getattr__(key)  # type: ignore
        except AttributeError:
            value = getattr(self._core_model, key)
            if key not in self._not_copy_key_list:
                value = copy.deepcopy(value)
                setattr(self, key, value)
            return value

    @classmethod
    def get_core_model(cls, core_model: "Union[PaitCoreProxyModel, PaitCoreModel]") -> "PaitCoreModel":
        if isinstance(core_model, cls):
            return core_model._core_model
        return core_model  # type: ignore


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

    def get_core_model(
        self,
        app_name: str,
        pait_id: str,
        path: str,
        openapi_path: str,
        method_set: Set[str],
        route_name: str = "",
        overwrite_already_exists_data: bool = False,
    ) -> Optional["PaitCoreModel"]:
        """Route handle information supplemented by load_app
        Note: 返回的是一个PaitCordModel的代理类，不是PaitCordModel本身，所以不要直接修改返回的对象
        Note:
            The return is a proxy class of a PaitCordModel, not the PaitCordModel itself,
            so do not modify the returned object directly.

            But you can get the original PaitCordModel object through the provided `get_core_model` method
        """
        if pait_id not in self.pait_id_dict[app_name]:
            logging.warning(f"load path:{path} fail, pait id:{pait_id}")
            return None

        model: "PaitCoreModel" = self.pait_id_dict[app_name][pait_id]
        method_list = sorted(list(method_set or set()), reverse=True)
        if not model.path or overwrite_already_exists_data:
            model.path = path
            model.openapi_path = openapi_path
            model.method_list = method_list
            if route_name:
                model.operation_id = route_name

        if route_name:
            operation_id = route_name
        else:
            operation_id = model.operation_id
        return PaitCoreProxyModel(core_model=model, operation_id=operation_id)  # type: ignore

    def __bool__(self) -> bool:
        return bool(self.pait_id_dict)
