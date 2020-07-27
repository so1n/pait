import inspect
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


def get_class_that_defined_method(func: Callable) -> Type:
    """
    copy from: https://stackoverflow.com/questions/3589311/get-defining-class-of-unbound-method-object-in-python-3/25959545#25959545
    """
    return getattr(inspect.getmodule(func), func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])


def async_params_verify(web: 'Type[BaseAsyncHelper]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)

        @wraps(func)
        async def dispatch(*args, **kwargs):
            class_ = get_class_that_defined_method(func)
            request = None
            new_args = []
            for param in args:
                if type(param) == web.RequestType:
                    request = param
                    # in cbv, request parameter will only appear after the self parameter
                    break
                elif isinstance(param, class_):
                    new_args.append(param)
            try:
                dispatch_web: BaseAsyncHelper = web(request)
                func_args, func_kwargs = await async_func_param_handle(dispatch_web, func_sig)
                new_args.extend(func_args)
                return await func(*new_args, **func_kwargs)
            except Exception as e:
                # TODO
                raise e from e
        return dispatch
    return wrapper


def sync_params_verify(web: 'Type[BaseHelper]'):
    def wrapper(func: Callable):
        func_sig: FuncSig = get_func_sig(func)

        @wraps(func)
        def dispatch(*args, **kwargs):
            try:
                class_ = get_class_that_defined_method(func)
                request = None
                new_args = []
                for param in args:
                    if type(param) == web.RequestType:
                        request = param
                        # in cbv, request parameter will only appear after the self parameter
                        break
                    elif isinstance(param, class_):
                        new_args.append(param)
                dispatch_web: BaseHelper = web(request)
                func_args, func_kwargs = func_param_handle(dispatch_web, func_sig)
                new_args.extend(func_args)
                return func(*new_args, **func_kwargs)
            except Exception as e:
                # TODO
                raise e from e
        return dispatch
    return wrapper
