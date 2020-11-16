import logging
from dataclasses import dataclass
from typing import Callable, Dict, Set, Tuple, Optional


@dataclass()
class PaitCoreModel(object):
    func: Callable                           # func object
    func_name: str                           # func name
    pait_id: str                             # pait id(in runtime)

    method_set: Optional[Set[str]] = None    # request method set
    path: Optional[str] = None               # request path
    operation_id: Optional[str] = None       # operation id(in route table)

    author: Optional[Tuple[str]] = None      # author
    desc: Optional[str] = None               # description
    status: Optional[str] = None             # api status. example: test, release
    tag: str = 'root'                        # request tag


class PaitData(object):
    def __init__(self):
        self.pait_id_dict: Dict[str, 'PaitCoreModel'] = {}

    def register(self, pait_info_model: 'PaitCoreModel'):
        pait_id: str = pait_info_model.pait_id
        self.pait_id_dict[pait_id] = pait_info_model

    def add_route_info(self, pait_id: str, path: str, method_set: Set[str], route_name: str, endpoint: Callable):
        if pait_id in self.pait_id_dict:
            self.pait_id_dict[pait_id].path = path
            self.pait_id_dict[pait_id].method_set = method_set
            self.pait_id_dict[pait_id].operation_id = route_name
        else:
            logging.warning(f'loan path:{path} fail, endpoint:{endpoint}, pait id:{pait_id}')

    def __getitem__(self, item):
        return self.pait_id_dict[item]

    def __setitem__(self, key: str, value: 'PaitCoreModel'):
        self.pait_id_dict[key] = value

    def __bool__(self):
        return bool(self.pait_id_dict)
