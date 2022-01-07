from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from json import JSONEncoder
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

from pydantic import BaseConfig

from pait.model.response import PaitBaseResponseModel
from pait.model.status import PaitStatus
from pait.util import json_type_default_value_dict as pait_json_type_default_value_dict
from pait.util import python_type_default_value_dict as pait_python_type_default_value_dict


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if type(obj) == date:
            return datetime.strptime(str(obj), "%Y-%m-%d")
        elif isinstance(obj, datetime):
            return int(obj.timestamp())
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
        self.enable_mock_response_filter_fn: Optional[Callable[[Type[PaitBaseResponseModel]], bool]] = None
        self.block_http_method_set: Set[str] = set()
        self.default_response_model_list: List[Type[PaitBaseResponseModel]] = []
        self.json_encoder: Type[JSONEncoder] = CustomJSONEncoder
        self.default_pydantic_model_config: Type[BaseConfig] = BaseConfig
        self.tag_dict: Dict[str, str] = {}

    def __setattr__(self, key: Any, value: Any) -> None:
        if not self.__initialized:
            super().__setattr__(key, value)
        else:
            raise RuntimeError("Can not set new value in runtime")

    def init_config(
        self,
        author: Optional[Tuple[str, ...]] = None,
        status: Optional[PaitStatus] = None,
        default_response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        enable_mock_response_filter_fn: Optional[Callable[[Type[PaitBaseResponseModel]], bool]] = None,
        block_http_method_set: Optional[Set[str]] = None,
        json_type_default_value_dict: Optional[Dict[str, Any]] = None,
        python_type_default_value_dict: Optional[Dict[type, Any]] = None,
        json_encoder: Optional[Type[JSONEncoder]] = None,
        default_pydantic_model_config: Optional[Type[BaseConfig]] = None,
    ) -> None:
        """
        :param author:  Only @pait(author=None) will be called to change the configuration
        :param status:  Only @pait(status=None) will be called to change the configuration
        :param default_response_model_list: Add a default response structure for all routing handles
        :param enable_mock_response_filter_fn:
            There are multiple response bodies in response_list, you can filter by changing the function
        :param block_http_method_set:
            Under normal circumstances, pait.load_app can obtain the http method of the routing handle.
            However, some application frameworks such as flask will automatically add optional http methods
             to the handle, which is great, but you may not want to use them in pait, and pait will not
             automatically recognize them, so you can use parameters to disable certain http method
        :param json_type_default_value_dict: Configure default values for each json type
        :param python_type_default_value_dict: Configure default values for each python type
        :param json_encoder: Define certain types of serialization rules
        :param default_pydantic_model_config: pait route gen pydantic model default config
        :return:
        """
        if author:
            self.author = author
        if status:
            self.status = status
        if default_response_model_list:
            self.default_response_model_list = default_response_model_list
        if enable_mock_response_filter_fn:
            self.enable_mock_response_filter_fn = enable_mock_response_filter_fn
        if block_http_method_set:
            self.block_http_method_set = block_http_method_set
        if json_type_default_value_dict:
            pait_json_type_default_value_dict.update(json_type_default_value_dict)
        if python_type_default_value_dict:
            pait_python_type_default_value_dict.update(python_type_default_value_dict)
        if json_encoder:
            self.json_encoder = json_encoder
        if default_pydantic_model_config:
            self.default_pydantic_model_config = default_pydantic_model_config

        self.__initialized = True

    @property
    def initialized(self) -> bool:
        """Judge whether it has been initialized, it can only be initialized once per run"""
        return self.__initialized
