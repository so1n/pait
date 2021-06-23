from enum import Enum


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
