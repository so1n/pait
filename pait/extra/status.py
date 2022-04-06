from typing import Dict

from pait.model.status import PaitStatus

__all__ = ["get_color"]
_pait_status_num_dict: Dict[PaitStatus, int] = {i: index for index, i in enumerate(PaitStatus.__members__.values())}


def get_color(pait_status: PaitStatus) -> str:
    pait_status_num: int = _pait_status_num_dict[pait_status]
    if pait_status_num <= _pait_status_num_dict[PaitStatus.dev]:
        return "#DC143C"
    elif pait_status_num <= _pait_status_num_dict[PaitStatus.test]:
        return "#00BFFF"
    elif pait_status_num <= _pait_status_num_dict[PaitStatus.release]:
        return "#32CD32"
    else:
        return "#DC143C"
