from enum import Enum

__all__ = ["PaitStatus"]


class PaitStatus(Enum):
    """Interface life cycle"""

    undefined = "undefined"
    # APIs are under development and change frequently
    design = "design"
    dev = "dev"

    # The API has been developed, but a few changes will still be made
    integration = "integration"
    complete = "complete"
    test = "test"

    # The API is ready and fully tested and ready to be release
    pre_release = "pre_release"
    release = "release"

    # API exceptions or version iterations in the production environment need to be archived
    abnormal = "abnormal"
    maintenance = "maintenance"
    archive = "archive"
    abandoned = "abandoned"

    def is_deprecated(self) -> bool:
        return self in (
            PaitStatus.abnormal,
            PaitStatus.maintenance,
            PaitStatus.archive,
            PaitStatus.abandoned,
        )
