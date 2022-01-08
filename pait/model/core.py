import logging
from typing import TYPE_CHECKING, Callable, List, Optional, Set, Tuple, Type

from pydantic import BaseConfig

from pait.model.response import PaitBaseResponseModel, PaitResponseModel
from pait.model.status import PaitStatus

if TYPE_CHECKING:
    from pait.app.base import BaseAppHelper


class PaitCoreModel(object):
    def __init__(
        self,
        func: Callable,
        app_helper_class: "Type[BaseAppHelper]",
        pre_depend_list: Optional[List[Callable]] = None,
        path: Optional[str] = None,
        openapi_path: Optional[str] = None,
        method_set: Optional[Set[str]] = None,
        operation_id: Optional[str] = None,
        func_name: Optional[str] = None,
        author: Optional[Tuple[str, ...]] = None,
        summary: Optional[str] = None,
        desc: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[str, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
    ):
        self._response_model_list: List[Type[PaitBaseResponseModel]] = []
        self.app_helper_class: "Type[BaseAppHelper]" = app_helper_class
        self.func: Callable = func  # route func
        self.pre_depend_list: List[Callable] = pre_depend_list or []
        self.qualname: str = func.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]
        self.pait_id: str = f"{self.qualname}_{id(func)}"
        setattr(func, "_pait_id", self.pait_id)
        self.path: str = path or ""  # request url path
        self.openapi_path: str = openapi_path or ""
        self._method_list: List[str] = sorted(list(method_set or set()))  # request method set
        self.func_name: str = func_name or func.__name__
        self.operation_id: str = operation_id or self.func_name  # route name
        self.author: Optional[Tuple[str, ...]] = author  # The main developer of this func
        self.summary: str = summary or ""
        self.desc: str = desc or func.__doc__ or ""  # desc of this func
        self.status: Optional[PaitStatus] = status  # Interface development progress (life cycle)
        self.group: str = group or "root"  # Which group this interface belongs to
        self.tag: Tuple[str, ...] = tag or ("default",)  # Interface tag
        self.func_path: str = ""
        self.block_http_method_set: Set[str] = set()
        self.enable_mock_response_filter_fn: Optional[Callable[[Type[PaitBaseResponseModel]], bool]] = None
        self.pydantic_model_config: Type[BaseConfig] = pydantic_model_config or BaseConfig

        if response_model_list:
            self.add_response_model_list(response_model_list)

    @property
    def method_list(self) -> List[str]:
        return self._method_list

    @method_list.setter
    def method_list(self, method_list: List[str]) -> None:
        _temp_set: Set[str] = set(self._method_list) | set(method_list)
        _temp_set.difference_update(self.block_http_method_set)
        self._method_list = sorted(list(_temp_set))

    @property
    def response_model_list(self) -> List[Type[PaitBaseResponseModel]]:
        return self._response_model_list

    def add_response_model_list(self, response_model_list: List[Type[PaitBaseResponseModel]]) -> None:
        for response_model in response_model_list:
            if response_model in self._response_model_list:
                continue
            if issubclass(response_model, PaitResponseModel):
                logging.warning(
                    f"Please replace {self.operation_id}'s response model {response_model}"
                    f" with {PaitBaseResponseModel}"
                )
            self._response_model_list.append(response_model)
