from enum import Enum
from typing import Dict


class PaitStatus(Enum):
    """Interface life cycle"""

    undefined = "undefined"
    # The interface is under development and will frequently change
    design = "design"
    dev = "dev"

    # The interface has been completed, but there may be some bugs
    integration = "integration"
    complete = "complete"
    test = "test"

    # The interface is online
    pre_release = "pre_release"
    release = "release"

    # The interface has been online, but needs to be offline for some reasons
    abnormal = "abnormal"
    maintenance = "maintenance"
    archive = "archive"
    abandoned = "abandoned"


_pait_status_num_dict: Dict[PaitStatus, int] = {i: index for index, i in enumerate(PaitStatus.__members__.values())}


def pait_status_color(pait_status: PaitStatus) -> str:
    pait_status_num: int = _pait_status_num_dict[pait_status]
    if pait_status_num <= _pait_status_num_dict[PaitStatus.dev]:
        return "#DC143C"
    elif pait_status_num <= _pait_status_num_dict[PaitStatus.test]:
        return "#00BFFF"
    elif pait_status_num <= _pait_status_num_dict[PaitStatus.release]:
        return "#32CD32"
    else:
        return "#DC143C"
