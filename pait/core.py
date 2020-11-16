import inspect
from functools import wraps
from typing import Callable, Type, Union

from pait.app.base import (
    BaseAsyncAppDispatch,
    BaseAppDispatch,
)
from pait.g import pait_data
from pait.pait_info import PaitInfoModel
from pait.param_handle import (
    async_class_param_handle,
    async_func_param_handle,
    class_param_handle,
    func_param_handle
)
from pait.util import (
    FuncSig,
    get_func_sig,
)


def params_verify(app: 'Type[Union[BaseAppDispatch, BaseAsyncAppDispatch]]', tag: str = 'root'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)
        qualname = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]

        pait_id: str = f'{qualname}_{id(func)}'
        func._pait_id = pait_id
        pait_data.register(PaitInfoModel(func=func, func_name=func.__name__, pait_id=pait_id, tag=tag))

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def dispatch(*args, **kwargs):
                # only use in runtime
                class_ = getattr(inspect.getmodule(func), qualname)
                # real param handle
                dispatch_app: BaseAsyncAppDispatch = app(class_, args, kwargs)
                # auto gen param from request
                func_args, func_kwargs = await async_func_param_handle(dispatch_app, func_sig)
                # support sbv
                await async_class_param_handle(dispatch_app)
                return await func(*func_args, **func_kwargs)
            return dispatch
        else:
            @wraps(func)
            def dispatch(*args, **kwargs):
                # only use in runtime
                class_ = getattr(inspect.getmodule(func), qualname)
                # real param handle
                dispatch_app: BaseAppDispatch = app(class_, args, kwargs)
                # auto gen param from request
                func_args, func_kwargs = func_param_handle(dispatch_app, func_sig)
                # support sbv
                class_param_handle(dispatch_app)
                return func(*func_args, **func_kwargs)
            return dispatch
    return wrapper
