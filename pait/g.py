import logging
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Set


@dataclass()
class PaitInfoModel(object):
    func: Optional[Callable] = None          # func obeject
    func_name: Optional[str] = None          # func name
    method_set: Optional[Set[str]] = None    # request method set
    path: Optional[str] = None               # request path
    pait_id: Optional[str] = None            # pait id(in runtime)
    operation_id: Optional[str] = None       # operation id(in route table)


pait_id_dict: Dict[str, PaitInfoModel] = {}


def add_to_pait_name_dict(pait_id: str, path: str, method_set: Set[str], route_name: str, endpoint: Callable):
    if pait_id in pait_id_dict:
        pait_id_dict[pait_id].path = path
        pait_id_dict[pait_id].method_set = method_set
        pait_id_dict[pait_id].operation_id = route_name
    else:
        logging.warning(f'loan path:{path} fail, endpoint:{endpoint}, pait id:{pait_id}')