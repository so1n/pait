from typing import Any

from pait.data import PaitData
from pait.model.config import Config

__all__ = ["config", "pait_data"]

# In order to reduce the intrusion of pait to the application framework,
# pait conducts data interaction through PaitData and Config
pait_data: PaitData = PaitData()
config: Config = Config()

# pait_data and config cannot refer to each other within the module
# By replacing the init_config function, the user can change the pait_data data when calling config.init_config
_real_config_init_config_method = config.init_config


def _after_config_init(*args: Any, **kwargs: Any) -> None:
    _real_config_init_config_method(*args, **kwargs)
    for app_name, real_pait_id_dict in pait_data.pait_id_dict.items():
        for pait_id, pait_info_model in real_pait_id_dict.items():
            if not pait_info_model.author:
                pait_info_model.author = config.author
            if not pait_info_model.status:
                pait_info_model.status = config.status

            if config.default_response_model_list:
                pait_info_model.response_model_list.extend(config.default_response_model_list)
            if config.enable_mock_response:
                pait_info_model.func = pait_info_model.return_mock_response


setattr(config, config.init_config.__name__, _after_config_init)
