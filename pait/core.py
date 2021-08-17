import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from pait.app.base import BaseAppHelper
from pait.exceptions import CheckValueError
from pait.g import pait_data
from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus
from pait.param_handle import async_class_param_handle, async_func_param_handle, class_param_handle, func_param_handle
from pait.util import FuncSig, gen_tip_exc, get_func_sig


def _check_at_most_one_of(at_most_one_of_list: List[List[str]], func_kwargs: Dict[str, Any]) -> None:
    """Check whether each group of parameters appear at the same time"""
    for at_most_one_of in at_most_one_of_list:
        if len([i for i in at_most_one_of if func_kwargs.get(i, None) is not None]) > 1:
            raise CheckValueError(f"requires at most one of param {' or '.join(at_most_one_of)}")


def _check_required_by(required_by: Dict[str, List[str]], func_kwargs: Dict[str, Any]) -> None:
    """Check dependencies between parameters"""
    for pre_param, param_list in required_by.items():
        if pre_param not in func_kwargs:
            continue
        for param in param_list:
            if func_kwargs.get(param, None) is not None and func_kwargs[pre_param] is None:
                raise CheckValueError(f"{pre_param} requires param {' and '.join(param_list)}, which if not none")


def pait(
    app_helper_class: "Type[BaseAppHelper]",
    make_mock_response_fn: Callable[[Type[PaitResponseModel]], Any],
    # param check
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
        func_sig: FuncSig = get_func_sig(func)

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
        )
        pait_data.register(app_name, pait_core_model)

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def dispatch(*args: Any, **kwargs: Any) -> Callable:
                try:
                    # only use in runtime, support cbv
                    class_ = getattr(inspect.getmodule(func), pait_core_model.qualname)
                    # real param handle
                    app_helper: BaseAppHelper = app_helper_class(class_, args, kwargs)  # type: ignore
                    # auto gen param from request
                    func_args, func_kwargs = await async_func_param_handle(app_helper, func_sig)
                    # support sbv
                    await async_class_param_handle(app_helper)
                    # param check
                    if at_most_one_of_list:
                        _check_at_most_one_of(at_most_one_of_list, func_kwargs)
                    if required_by:
                        _check_required_by(required_by, func_kwargs)
                except Exception as e:
                    raise e from gen_tip_exc(func, e)
                return await pait_core_model.func(*func_args, **func_kwargs)

            return dispatch
        else:

            @wraps(func)
            def dispatch(*args: Any, **kwargs: Any) -> Callable:
                try:
                    # only use in runtime
                    class_ = getattr(inspect.getmodule(func), pait_core_model.qualname)
                    # real param handle
                    app_helper = app_helper_class(class_, args, kwargs)  # type: ignore
                    # auto gen param from request
                    func_args, func_kwargs = func_param_handle(app_helper, func_sig)
                    # support sbv
                    class_param_handle(app_helper)
                    # param check
                    if at_most_one_of_list:
                        _check_at_most_one_of(at_most_one_of_list, func_kwargs)
                    if required_by:
                        _check_required_by(required_by, func_kwargs)
                except Exception as e:
                    raise e from gen_tip_exc(func, e)
                return pait_core_model.func(*func_args, **func_kwargs)

            return dispatch

    return wrapper
