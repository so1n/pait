from typing import Callable, List, Optional, Set, Tuple, Type

from pait.g import config
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus


class PaitCoreModel(object):
    def __init__(
        self,
        func: Callable,
        pait_id: str,
        path: Optional[str] = None,
        method_set: Optional[Set[str]] = None,
        operation_id: Optional[str] = None,
        func_name: Optional[str] = None,
        author: Optional[Tuple[str, ...]] = None,
        summary: Optional[str] = None,
        desc: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[str, ...]] = None,
        response_model_list: Optional[List[Type[PaitResponseModel]]] = None,
    ):
        self.func: Callable = func  # route func
        self.pait_id: str = pait_id  # qualname + func hash id
        self.path: str = path or ""  # request url path
        self.method_list: List[str] = sorted(list(method_set or set()))  # request method set
        self.func_name: str = func_name or func.__name__
        self.operation_id: str = operation_id or self.func_name  # route name
        self._author: Optional[Tuple[str, ...]] = author  # The main developer of this func
        self.summary: str = summary or ""
        self.desc: str = desc or func.__doc__ or ""  # desc of this func
        self._status: Optional[PaitStatus] = status  # Interface development progress (life cycle)
        self.group: str = group or "root"  # Which group this interface belongs to
        self.tag: Tuple[str, ...] = tag or ("default",)  # Interface tag
        self._response_model_list: List[Type[PaitResponseModel]] = response_model_list or []
        self.func_path: str = ""

    @property
    def author(self) -> Tuple[str, ...]:
        return self._author or config.author

    @property
    def status(self) -> PaitStatus:
        return self._status or config.status

    @property
    def response_model_list(self) -> List[Type[PaitResponseModel]]:
        if config.default_response_model_list:
            return self._response_model_list + config.default_response_model_list
        else:
            return self._response_model_list
