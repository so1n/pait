from functools import wraps
from typing import Callable, Type

from pait.func_param_handle import (
    async_func_param_handle,
    func_param_handle
)
from pait.util import (
    BaseAsyncHelper,
    BaseHelper,
    FuncSig,
    get_func_sig,
)


def async_params_verify(web: 'Type[BaseAsyncHelper]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)

        @wraps(func)
        async def dispatch(request, *args, **kwargs):
            try:
                dispatch_web: BaseAsyncHelper = web(request)
                func_args, func_kwargs = await async_func_param_handle(dispatch_web, func_sig)
                return await func(*func_args, **func_kwargs)
            except Exception as e:
                # TODO
                raise e from e
        return dispatch
    return wrapper


def sync_params_verify(web: 'Type[BaseHelper]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)

        @wraps(func)
        def dispatch(request, *args, **kwargs):
            try:
                dispatch_web: BaseHelper = web(request)
                func_args, func_kwargs = func_param_handle(dispatch_web, func_sig)
                return func(*func_args, **func_kwargs)
            except Exception as e:
                # TODO
                raise e from e
        return dispatch
    return wrapper
