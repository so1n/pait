from typing import Any, List, NoReturn, Optional, Tuple, Type

from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus


class Config(object):
    __initialized: bool = False

    def __init__(self) -> None:
        self.author: Tuple[str, ...] = ("",)
        self.status: PaitStatus = PaitStatus.undefined
        self.default_response_model_list: List[Type[PaitResponseModel]] = []

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
    ) -> None:
        self.author = author
        self.status = status
        self.default_response_model_list = default_response_model_list or []

        self.__initialized = True
