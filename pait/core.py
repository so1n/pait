import copy
import inspect
from functools import wraps
from typing import Any, Callable, List, Optional, Set, Tuple, Type

from pait.app.base import BaseAppHelper
from pait.g import config, pait_data
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus
from pait.param_handle import async_class_param_handle, async_func_param_handle, class_param_handle, func_param_handle
from pait.util import FuncSig, get_func_sig


def pait(
    app_helper_class: "Type[BaseAppHelper]",
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: Optional[List[Type[PaitResponseModel]]] = None,
) -> Callable:
    if not isinstance(app_helper_class, type):
        raise TypeError(f"{app_helper_class} must be class")
    if not issubclass(app_helper_class, BaseAppHelper):
        raise TypeError(f"{app_helper_class} must sub {BaseAppHelper.__class__.__name__}")
    app_name: str = getattr(app_helper_class, "app_name", "")

    def wrapper(func: Callable) -> Callable:
        func_sig: FuncSig = get_func_sig(func)
        qualname = func.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]

        pait_id: str = f"{qualname}_{id(func)}"
        setattr(func, "_pait_id", pait_id)
        pait_data.register(
            app_name,
            PaitCoreModel(
                author=author,
                desc=desc,
                summary=summary,
                func=func,
                pait_id=pait_id,
                status=status,
                group=group,
                tag=tag,
                response_model_list=response_model_list,
            ),
        )

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def dispatch(*args: Any, **kwargs: Any) -> Callable:
                # only use in runtime, support cbv
                class_ = getattr(inspect.getmodule(func), qualname)
                # real param handle
                app_helper: BaseAsyncAppHelper = app_helper_class(class_, args, kwargs)  # type: ignore
                # auto gen param from request
                func_args, func_kwargs = await async_func_param_handle(app_helper, func_sig)
                # support sbv
                await async_class_param_handle(app_helper)
                return await func(*func_args, **func_kwargs)

            return dispatch
        else:

            @wraps(func)
            def dispatch(*args: Any, **kwargs: Any) -> Callable:
                # only use in runtime
                class_ = getattr(inspect.getmodule(func), qualname)
                # real param handle
                app_helper: BaseSyncAppHelper = app_helper_class(class_, args, kwargs)  # type: ignore
                # auto gen param from request
                func_args, func_kwargs = func_param_handle(app_helper, func_sig)
                # support sbv
                class_param_handle(app_helper)
                return func(*func_args, **func_kwargs)

            return dispatch

    return wrapper


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
        self._response_model_list: Optional[List[Type[PaitResponseModel]]] = response_model_list
        self.func_path: str = ""

    @property
    def author(self) -> Tuple[str, ...]:
        return self._author or config.author

    @property
    def status(self) -> PaitStatus:
        return self._status or config.status

    @property
    def response_model_list(self) -> List[Type[PaitResponseModel]]:
        if self._response_model_list:
            response_model_list: List[Type[PaitResponseModel]] = copy.deepcopy(self._response_model_list)
        else:
            response_model_list = []
        response_model_list.extend(config.default_response_model_list)
        return response_model_list
