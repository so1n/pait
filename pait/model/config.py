from json import JSONEncoder
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type

from pait.exceptions import TipException
from pait.model.response import BaseResponseModel
from pait.model.response import http_status_code_dict as pait_http_status_code_dict
from pait.model.status import PaitStatus
from pait.util import json_type_default_value_dict as pait_json_type_default_value_dict
from pait.util import python_type_default_value_dict as pait_python_type_default_value_dict
from pait.util.encoder import CustomJSONEncoder

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

APPLY_FN = Callable[["PaitCoreModel"], None]


__all__ = ["Config", "APPLY_FN"]


class Config(object):
    """
    Provide pait parameter configuration, the init_config method is valid only before the application service is started
    """

    __initialized: bool = False

    def __init__(self) -> None:
        self.author: Tuple[str, ...] = tuple()
        self.status: PaitStatus = PaitStatus.undefined
        self.default_response_model_list: List[Type[BaseResponseModel]] = []
        self.json_encoder: Type[JSONEncoder] = CustomJSONEncoder
        self.tag_dict: Dict[str, str] = {}
        self.apply_func_list: List[APPLY_FN] = []
        self.tip_exception_class: Optional[Type[TipException]] = TipException

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
        apply_func_list: Optional[List[APPLY_FN]] = None,
        tip_exception_class: Optional[Type[TipException]] = TipException,
        http_status_code_dict: Optional[Dict[int, str]] = None,
    ) -> None:
        """
        :param author:  Only @pait(author=None) will be called to change the configuration
        :param status:  Only @pait(status=None) will be called to change the configuration
        :param json_type_default_value_dict: Configure default values for each json type
        :param python_type_default_value_dict: Configure default values for each python type
        :param json_encoder: Define certain types of serialization rules
        :param apply_func_list: List of functions for application configuration
        :param tip_exception_class: Custom tip exception class
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
        if http_status_code_dict:
            pait_http_status_code_dict.update(**http_status_code_dict)  # type:ignore[misc]

        if json_encoder:
            self.json_encoder = json_encoder
        if apply_func_list:
            self.apply_func_list = apply_func_list
        if tip_exception_class is not self.tip_exception_class:
            self.tip_exception_class = tip_exception_class
        self.__initialized = True

    @property
    def initialized(self) -> bool:
        """Judge whether it has been initialized, it can only be initialized once per run"""
        return self.__initialized

    @property
    def json_type_default_value_dict(self) -> Dict[str, Any]:
        return pait_json_type_default_value_dict

    @property
    def python_type_default_value_dict(self) -> Dict:
        return pait_python_type_default_value_dict
