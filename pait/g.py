from dataclasses import dataclass
from typing import Callable, Dict, Optional, Set


@dataclass()
class PaitModel(object):
    func: Optional[Callable] = None
    method_set: Optional[Set[str]] = None
    path: Optional[str] = None
    pait_name: Optional[str] = None


pait_name_dict: Dict[str, PaitModel] = {}