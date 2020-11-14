from dataclasses import dataclass
from typing import Callable, Dict, Optional, Set


@dataclass()
class PaitInfoModel(object):
    func: Optional[Callable] = None
    func_name: Optional[str] = None
    method_set: Optional[Set[str]] = None
    path: Optional[str] = None
    pait_name: Optional[str] = None


pait_name_dict: Dict[str, PaitInfoModel] = {}