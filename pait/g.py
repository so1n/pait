import logging
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Set


@dataclass()
class PaitInfoModel(object):
    func: Optional[Callable] = None
    func_name: Optional[str] = None
    method_set: Optional[Set[str]] = None
    path: Optional[str] = None
    pait_name: Optional[str] = None
    operation_id: Optional[str] = None


pait_name_dict: Dict[str, PaitInfoModel] = {}


def add_to_pait_name_dict(pait_name: str, path: str, method_set: Set[str], route_name: str, endpoint: Callable):
    if pait_name in pait_name_dict:
        pait_name_dict[pait_name].path = path
        pait_name_dict[pait_name].method_set = method_set
        pait_name_dict[pait_name].operation_id = route_name
    else:
        logging.warning(f'loan path:{path} fail, endpoint:{endpoint}, pait name:{pait_name}')