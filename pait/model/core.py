import asyncio
import inspect
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Set, Tuple, Type

from pydantic import BaseConfig

from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus

if TYPE_CHECKING:
    from pait.app.base import BaseAppHelper


class PaitCoreModel(object):
    def __init__(
        self,
        func: Callable,
        app_helper_class: "Type[BaseAppHelper]",
        make_mock_response_fn: Callable[[Type[PaitResponseModel]], Any],
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
        response_model_list: Optional[List[Type[PaitResponseModel]]] = None,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
    ):
        self.app_helper_class: "Type[BaseAppHelper]" = app_helper_class
        self.make_mock_response_fn: Callable[[Type[PaitResponseModel]], Any] = make_mock_response_fn
        self.func: Callable = func  # route func
        self.pait_func: Callable = func  # route func， If `mock_response` is used, this function will be replaced
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
        self.response_model_list: List[Type[PaitResponseModel]] = response_model_list or []
        self.func_path: str = ""
        self.block_http_method_set: Set[str] = set()
        self.enable_mock_response_filter_fn: Optional[Callable[[Type[PaitResponseModel]], bool]] = None
        self.pydantic_model_config: Type[BaseConfig] = pydantic_model_config or BaseConfig

    # @property
    # def author(self) -> Tuple[str, ...]:
    #     return self._author or config.author
    #
    # @property
    # def status(self) -> PaitStatus:
    #     return self._status or config.status
    #
    # @property
    # def func(self) -> Callable:
    #     if config.enable_mock_response:
    #         return self.return_mock_response
    #     return self._func

    @property
    def method_list(self) -> List[str]:
        return self._method_list

    @method_list.setter
    def method_list(self, method_list: List[str]) -> None:
        _temp_set: Set[str] = set(self._method_list) | set(method_list)
        _temp_set.difference_update(self.block_http_method_set)
        self._method_list = sorted(list(_temp_set))

    def return_mock_response(self, *args: Any, **kwargs: Any) -> Any:
        if not self.response_model_list:
            raise RuntimeError(f"{self.func} can not set response model")
        pait_response: Optional[Type[PaitResponseModel]] = None
        if self.enable_mock_response_filter_fn:
            for _pait_response in self.response_model_list:
                if self.enable_mock_response_filter_fn(_pait_response):
                    pait_response = _pait_response
                    break
        if not pait_response:
            pait_response = self.response_model_list[0]

        # fix tornado
        if self.app_helper_class.app_name == "tornado":
            setattr(pait_response, "handle", args[0])
        resp: Any = self.make_mock_response_fn(pait_response)
        # support async def
        if inspect.iscoroutinefunction(self.func):
            future: asyncio.Future = asyncio.Future()
            future.set_result(resp)
            resp = future
        return resp

    # @property
    # def response_model_list(self) -> List[Type[PaitResponseModel]]:
    #     if config.default_response_model_list:
    #         return self._response_model_list + config.default_response_model_list
    #     else:
    #         return self._response_model_list
