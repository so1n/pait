from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pait.model.config import Config
    from pait.model.core import PaitCoreModel


def sync_config_data_to_pait_core_model(config: "Config", pait_core_model: "PaitCoreModel", **kwargs: Any) -> None:
    if not pait_core_model.author:
        pait_core_model.author = config.author
    if not pait_core_model.status:
        pait_core_model.status = config.status

    if config.default_response_model_list:
        pait_core_model.response_model_list.extend(config.default_response_model_list)
    if config.enable_mock_response_filter_fn:
        pait_core_model.enable_mock_response_filter_fn = config.enable_mock_response_filter_fn
    if kwargs.get("enable_mock_response", False) or config.enable_mock_response:
        pait_core_model.pait_func = pait_core_model.return_mock_response
