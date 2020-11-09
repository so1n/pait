import inspect
from functools import wraps
from typing import Callable, Type

from pait.app.base import (
    BaseAsyncAppDispatch,
    BaseAppDispatch,
)
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


def async_params_verify(app: 'Type[BaseAsyncAppDispatch]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)
        qualname = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]

        @wraps(func)
        async def dispatch(*args, **kwargs):
            # real param handle
            class_ = getattr(inspect.getmodule(func), qualname)
            dispatch_app: BaseAsyncAppDispatch = app(class_, args, kwargs)

            func_args, func_kwargs = await async_func_param_handle(dispatch_app, func_sig)
            await async_class_param_handle(dispatch_app)
            return await func(*func_args, **func_kwargs)
        return dispatch
    return wrapper


def sync_params_verify(app: 'Type[BaseAppDispatch]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)
        qualname = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]

        @wraps(func)
        def dispatch(*args, **kwargs):
            # real param handle
            class_ = getattr(inspect.getmodule(func), qualname)
            dispatch_app: BaseAppDispatch = app(class_, args, kwargs)

            func_args, func_kwargs = func_param_handle(dispatch_app, func_sig)
            class_param_handle(dispatch_app)
            return func(*func_args, **func_kwargs)
        return dispatch
    return wrapper
