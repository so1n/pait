from typing import TYPE_CHECKING, Any

from pait.model.core import DefaultValue
from pait.model.status import PaitStatus

if TYPE_CHECKING:
    from pait.model.config import Config
    from pait.model.core import PaitCoreModel


__all__ = ["sync_config_data_to_pait_core_model"]


def sync_config_data_to_pait_core_model(config: "Config", pait_core_model: "PaitCoreModel", **kwargs: Any) -> None:
    """Synchronize the config data to the corresponding pait core model"""

    if not pait_core_model.author and config.author:
        pait_core_model.author = config.author
    if not pait_core_model.status or pait_core_model.status is PaitStatus.undefined:
        pait_core_model.status = config.status
    if not pait_core_model.response_model_list:
        pait_core_model.add_response_model_list(config.default_response_model_list)
    if (
        pait_core_model.tip_exception_class is DefaultValue.tip_exception_class
        and config.tip_exception_class is not DefaultValue.tip_exception_class
    ):
        pait_core_model.tip_exception_class = config.tip_exception_class

    if config.apply_func_list:
        for apply_func in config.apply_func_list:
            apply_func(pait_core_model)
