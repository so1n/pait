import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from pait.app.base import BaseAppHelper
from pait.g import pait_data
from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus
from pait.param_handle import AsyncParamHandler, ParamHandler


def pait(
    app_helper_class: "Type[BaseAppHelper]",
    make_mock_response_fn: Callable[[Type[PaitResponseModel]], Any],
    # param check
    pre_depend_list: Optional[List[Callable]] = None,
    at_most_one_of_list: Optional[List[List[str]]] = None,
    required_by: Optional[Dict[str, List[str]]] = None,
    # doc
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: Optional[List[Type[PaitResponseModel]]] = None,
) -> Callable:
    if not isinstance(app_helper_class, type):
        raise TypeError(f"{app_helper_class} must be class")
    if not issubclass(app_helper_class, BaseAppHelper):
        raise TypeError(f"{app_helper_class} must sub from {BaseAppHelper.__class__.__name__}")
    app_name: str = app_helper_class.app_name

    def wrapper(func: Callable) -> Callable:

        pait_core_model: PaitCoreModel = PaitCoreModel(
            author=author,
            app_helper_class=app_helper_class,
            make_mock_response_fn=make_mock_response_fn,
            desc=desc,
            summary=summary,
            func=func,
            func_name=name,
            status=status,
            group=group,
            tag=tag,
            response_model_list=response_model_list,
            pre_depend_list=pre_depend_list,
        )
        pait_data.register(app_name, pait_core_model)

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def dispatch(*args: Any, **kwargs: Any) -> Callable:
                async with AsyncParamHandler(
                    app_helper_class,
                    func,
                    at_most_one_of_list=at_most_one_of_list,
                    pre_depend_list=pre_depend_list,
                    required_by=required_by,
                    args=args,
                    kwargs=kwargs,
                ) as p:
                    return await pait_core_model.func(*p.args, **p.kwargs)

            return dispatch
        else:

            @wraps(func)
            def dispatch(*args: Any, **kwargs: Any) -> Callable:
                with ParamHandler(
                    app_helper_class,
                    func,
                    at_most_one_of_list=at_most_one_of_list,
                    pre_depend_list=pre_depend_list,
                    required_by=required_by,
                    args=args,
                    kwargs=kwargs,
                ) as p:
                    return pait_core_model.func(*p.args, **p.kwargs)

            return dispatch

    return wrapper
