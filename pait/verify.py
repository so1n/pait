import inspect
from functools import wraps
from typing import Any, Callable, Tuple, Type

from pait.web.base import (
    BaseAsyncHelper,
    BaseHelper,
)
from pait.func_param_handle import (
    async_func_param_handle,
    func_param_handle
)
from pait.util import (
    FuncSig,
    get_func_sig,
)


def args_handle(func: Callable, qualname: str, args: Tuple[Any, ...], web: 'Type[BaseHelper]'):
    class_ = getattr(inspect.getmodule(func), qualname)
    request = None
    new_args = []
    for param in args:
        if type(param) == web.RequestType:
            request = param
            # in cbv, request parameter will only appear after the self parameter
            break
        elif isinstance(param, class_):
            new_args.append(param)
    return request, new_args


def async_params_verify(web: 'Type[BaseAsyncHelper]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)
        qualname = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]

        @wraps(func)
        async def dispatch(*args, **kwargs):
            request, new_args = args_handle(func, qualname, args, web)
            try:
                dispatch_web: BaseAsyncHelper = web(request)
                func_args, func_kwargs = await async_func_param_handle(dispatch_web, func_sig)
                new_args.extend(func_args)
                kwargs.update(func_kwargs)
                return await func(*new_args, **kwargs)
            except Exception as e:
                # TODO
                raise e from e
        return dispatch
    return wrapper


def sync_params_verify(web: 'Type[BaseHelper]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)
        qualname = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]

        @wraps(func)
        def dispatch(*args, **kwargs):
            try:
                request, new_args = args_handle(func, qualname, args, web)
                dispatch_web: BaseHelper = web(request)
                func_args, func_kwargs = func_param_handle(dispatch_web, func_sig)
                new_args.extend(func_args)
                kwargs.update(func_kwargs)
                return func(*new_args, **kwargs)
            except Exception as e:
                # TODO
                raise e from e
        return dispatch
    return wrapper
