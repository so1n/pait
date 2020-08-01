from functools import wraps
from typing import Callable, Type

from pait.web.base import (
    BaseAsyncWebDispatch,
    BaseWebDispatch,
)
from pait.func_param_handle import (
    async_func_param_handle,
    func_param_handle
)
from pait.util import (
    FuncSig,
    get_func_sig,
)


def async_params_verify(web: 'Type[BaseAsyncWebDispatch]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)
        qualname = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]

        @wraps(func)
        async def dispatch(*args, **kwargs):
            try:
                dispatch_web: BaseAsyncWebDispatch = web(func, qualname, args, kwargs)
                func_args, func_kwargs = await async_func_param_handle(dispatch_web, func_sig)
                return await func(*func_args, **func_kwargs)
            except Exception as e:
                # TODO
                raise e from e
        return dispatch
    return wrapper


def sync_params_verify(web: 'Type[BaseWebDispatch]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)
        qualname = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]

        @wraps(func)
        def dispatch(*args, **kwargs):
            try:
                dispatch_web: BaseWebDispatch = web(func, qualname, args, kwargs)
                func_args, func_kwargs = func_param_handle(dispatch_web, func_sig)
                return func(*func_args, **func_kwargs)
            except Exception as e:
                # TODO
                raise e from e
        return dispatch
    return wrapper
