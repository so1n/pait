from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus


class Config(object):
    __initialized: bool = False

    def __init__(self) -> None:
        self.author: Tuple[str, ...] = ("",)
        self.status: PaitStatus = PaitStatus.undefined
        self.enable_mock_response: bool = False
        self.enable_mock_response_filter_fn: Optional[Callable[[Type[PaitResponseModel]], bool]] = None
        self.default_response_model_list: List[Type[PaitResponseModel]] = []
        self.json_type_default_value_dict: Dict[str, Any] = {
            "null": None,
            "bool": True,
            "boolean": True,
            "string": "",
            "number": 0.0,
            "float": 0.0,
            "integer": 0,
            "object": {},
            "array": [],
        }

    def __setattr__(self, key: Any, value: Any) -> None:
        if not self.__initialized:
            super().__setattr__(key, value)
        else:
            raise RuntimeError("Can not set new value in runtime")

    def init_config(
        self,
        author: Tuple[str, ...] = ("",),
        status: PaitStatus = PaitStatus.undefined,
        default_response_model_list: Optional[List[Type[PaitResponseModel]]] = None,
        json_type_default_value_dict: Optional[Dict[str, Any]] = None,
        enable_mock_response: bool = False,
        enable_mock_response_filter_fn: Optional[Callable[[Type[PaitResponseModel]], bool]] = None
    ) -> None:
        self.author = author
        self.status = status
        self.default_response_model_list = default_response_model_list or []
        if json_type_default_value_dict:
            self.json_type_default_value_dict.update(json_type_default_value_dict)
        self.enable_mock_response = enable_mock_response
        self.enable_mock_response_filter_fn = enable_mock_response_filter_fn

        self.__initialized = True
