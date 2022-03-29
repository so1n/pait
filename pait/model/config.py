from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from json import JSONEncoder
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple, Type

from pydantic import BaseConfig

from pait.model.response import PaitBaseResponseModel
from pait.model.status import PaitStatus
from pait.plugin.base import PluginManager
from pait.util import I18nTypedDict, change_local, http_method_tuple
from pait.util import i18n_config_dict as pait_i18n_config_dict
from pait.util import i18n_local as pait_i18n_local
from pait.util import json_type_default_value_dict as pait_json_type_default_value_dict
from pait.util import python_type_default_value_dict as pait_python_type_default_value_dict

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

APPLY_FN = Callable[["PaitCoreModel"], None]


def apply_default_response_model(
    response_model_list: List[Type[PaitBaseResponseModel]], match_key: str, match_value: Any
) -> APPLY_FN:
    """
    Add a default response structure for routing handles
    """
    for response_model in response_model_list:
        if response_model.is_core:
            raise ValueError(f"{response_model} is core response model can not set to default_response_model_list")

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_key, match_value):
            pait_core_model.add_response_model_list(response_model_list)

    return _apply


def apply_default_pydantic_model_config(
    pydantic_model_config: BaseConfig, match_key: str, match_value: Any
) -> APPLY_FN:
    """pait route gen pydantic model default config"""

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_key, match_value):
            pait_core_model.pydantic_model_config = pydantic_model_config

    return _apply


def apply_block_http_method_set(block_http_method_set: Set[str], match_key: str, match_value: Any) -> APPLY_FN:
    """
    Under normal circumstances, pait.load_app can obtain the http method of the routing handle.
     However, some application frameworks such as flask will automatically add optional http methods
     to the handle, which is great, but you may not want to use them in pait, and pait will not
     automatically recognize them, so you can use parameters to disable certain http method
    """
    for block_http_method in block_http_method_set:
        if block_http_method.lower() not in http_method_tuple:
            raise ValueError(f"Error http method: {block_http_method}")

    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_key, match_value):
            pait_core_model.block_http_method_set = block_http_method_set
            pait_core_model.method_list = pait_core_model.method_list

    return _apply


def apply_plugin(
    plugin_manager_fn_list: List[Callable[[], PluginManager]], match_key: str, match_value: Any
) -> APPLY_FN:
    def _apply(pait_core_model: "PaitCoreModel") -> None:
        if pait_core_model.match(match_key, match_value):
            pre_plugin_manager_list: List[PluginManager] = []
            post_plugin_manager_list: List[PluginManager] = []
            for plugin_manager_fn in plugin_manager_fn_list:
                plugin_manager: PluginManager = plugin_manager_fn()
                if plugin_manager.plugin_class.is_pre_core:
                    pre_plugin_manager_list.append(plugin_manager)
                else:
                    post_plugin_manager_list.append(plugin_manager)
            pait_core_model.add_plugin(pre_plugin_manager_list, post_plugin_manager_list)

    return _apply


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return int(obj.timestamp())
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        else:
            return super().default(obj)


class Config(object):
    """
    Provide pait parameter configuration, the init_config method is valid only before the application service is started
    """

    __initialized: bool = False

    def __init__(self) -> None:
        self.author: Tuple[str, ...] = ("",)
        self.status: PaitStatus = PaitStatus.undefined
        self.block_http_method_set: Set[str] = set()
        self.default_response_model_list: List[Type[PaitBaseResponseModel]] = []
        self.json_encoder: Type[JSONEncoder] = CustomJSONEncoder
        self.default_pydantic_model_config: Type[BaseConfig] = BaseConfig
        self.tag_dict: Dict[str, str] = {}
        self.i18n_local: str = pait_i18n_local
        self.apply_func_list: List[APPLY_FN] = []

    def __setattr__(self, key: Any, value: Any) -> None:
        if not self.__initialized:
            super().__setattr__(key, value)
        else:
            raise RuntimeError("Can not set new value in runtime")

    def init_config(
        self,
        author: Optional[Tuple[str, ...]] = None,
        status: Optional[PaitStatus] = None,
        json_type_default_value_dict: Optional[Dict[str, Any]] = None,
        python_type_default_value_dict: Optional[Dict[type, Any]] = None,
        json_encoder: Optional[Type[JSONEncoder]] = None,
        i18n_local: str = pait_i18n_local,
        i18n_config_dict: Optional[Dict[str, I18nTypedDict]] = None,
        apply_func_list: Optional[List[APPLY_FN]] = None,
    ) -> None:
        """
        :param author:  Only @pait(author=None) will be called to change the configuration
        :param status:  Only @pait(status=None) will be called to change the configuration
        :param json_type_default_value_dict: Configure default values for each json type
        :param python_type_default_value_dict: Configure default values for each python type
        :param json_encoder: Define certain types of serialization rules
        :return:
        """
        if self.__initialized:
            raise RuntimeError("Can not set new value in runtime")
        if author:
            self.author = author
        if status:
            self.status = status

        if json_type_default_value_dict:
            pait_json_type_default_value_dict.update(json_type_default_value_dict)
        if python_type_default_value_dict:
            pait_python_type_default_value_dict.update(python_type_default_value_dict)
        if json_encoder:
            self.json_encoder = json_encoder
        if i18n_local:
            change_local(i18n_local)
        if i18n_config_dict:
            pait_i18n_config_dict.update(i18n_config_dict)
        if apply_func_list:
            self.apply_func_list = apply_func_list
        self.__initialized = True

    @property
    def initialized(self) -> bool:
        """Judge whether it has been initialized, it can only be initialized once per run"""
        return self.__initialized
