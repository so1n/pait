import asyncio
import logging
import inspect

from typing import Any, Callable, Coroutine, Dict, List, Tuple, Optional, Union

from pydantic import BaseModel, create_model
from pait import field
from pait.util import FuncSig
from pait.web.base import (
    BaseAsyncHelper,
    BaseHelper
)


def single_field_handle(single_field_dict: Dict['inspect.Parameter', Any]) -> dict:
    annotation_dict = {}
    param_value_dict = {}
    for parameter, value in single_field_dict.items():
        annotation_dict[parameter.name] = (parameter.annotation, ...)
        param_value_dict[parameter.name] = value

    dynamic_model = create_model('DynamicFoobarModel', **annotation_dict)
    return dynamic_model(**param_value_dict).dict()


def extract_request_kwargs_data(
    parameter: inspect.Parameter,
    dispatch_web: 'BaseHelper'
) -> Union[Any, Coroutine, None]:
    # kwargs param
    # support model: pydantic.BaseModel = pait.field.BaseField()
    if isinstance(parameter.default, field.File):
        assert parameter.annotation is not dispatch_web.FileType, \
            f"File type must be {dispatch_web.FileType}"
    # Note: not use hasattr with LazyProperty (
    #   because hasattr calling getattr(obj, name) and catching AttributeError,
    # )
    dispatch_web_func:  Optional[Callable] = getattr(
        dispatch_web, parameter.default.__class__.__name__.lower()
    )
    if not dispatch_web_func:
        return
    return dispatch_web_func()


def set_value_to_args_param(
    parameter: inspect.Parameter,
    dispatch_web: 'BaseHelper',
    func_args: list
):
    # args param
    # Only support request param(def handle(request: Request))
    if parameter.annotation is dispatch_web.RequestType:
        func_args.append(dispatch_web.request)


def set_value_to_kwargs_param(
    parameter: inspect.Parameter,
    request_value,
    func_kwargs,
    single_field_dict,
    func_sig: FuncSig
):
    param_value = parameter.default
    annotation = parameter.annotation
    param_name = parameter.name

    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        # parse annotation is pydantic.BaseModel
        value = annotation(**request_value)
        func_kwargs[parameter.name] = value
    else:
        # parse annotation is python type and pydantic.field
        if type(param_value.key) is str and param_value.key in request_value:
            value = request_value.get(param_value.key, param_value.default)
        elif param_name in request_value:
            value = request_value.get(param_name, param_value.default)
        else:
            if param_value.default:
                value = param_value.default
            else:
                # Help users quickly locate the error code
                parameter_value_name = param_value.__class__.__name__
                def_title = 'def'
                if inspect.iscoroutinefunction(func_sig.func):
                    def_title = 'async def'
                param_str = (
                    f'{param_name}: {annotation} = {parameter_value_name}('
                    f'key={param_value.key}, default={param_value.default})'
                )
                logging.debug(f"""
{ def_title } {func_sig.func.__name__}(
    ...
    {param_str} <-- error
    ...
):
    pass
                              """)

                raise KeyError(
                    f'File "{inspect.getfile(func_sig.func)}",'
                    f' line {func_sig.func.__code__.co_firstlineno + 1},'
                    f' in {func_sig.func.__name__}\n'
                    f' kwargs param:{param_str} not found value,'
                    f' try use {parameter_value_name}(key={{key name}})'
                )

        single_field_dict[parameter] = value


async def async_func_param_handle(dispatch_web: 'BaseAsyncHelper', func_sig: FuncSig) -> Tuple[List, Dict]:
    func_args = []
    func_kwargs = {}
    single_field_dict: Dict['inspect.Parameter', Any] = {}
    for parameter in func_sig.param_list:
        if parameter.default != func_sig.sig.empty:
            # kwargs param
            # support model: pydantic.BaseModel = pait.field.BaseField()
            request_value = extract_request_kwargs_data(parameter, dispatch_web)

            if asyncio.iscoroutine(request_value):
                request_value = await request_value

            set_value_to_kwargs_param(
                parameter,
                request_value,
                func_kwargs,
                single_field_dict,
                func_sig
            )
        else:
            set_value_to_args_param(parameter, dispatch_web, func_args)

    # Support param: type = pait.field.BaseField()
    if single_field_dict:
        func_kwargs.update(single_field_handle(single_field_dict))

    return func_args, func_kwargs


def func_param_handle(dispatch_web: 'BaseHelper', func_sig: FuncSig) -> Tuple[List, Dict]:
    func_args: List[Any] = []
    func_kwargs: Dict[str, Any] = {}
    single_field_dict: Dict['inspect.Parameter', Any] = {}
    for parameter in func_sig.param_list:
        if parameter.default != func_sig.sig.empty:
            # kwargs param
            # support model: pydantic.BaseModel = pait.field.BaseField()
            request_value = extract_request_kwargs_data(parameter, dispatch_web)
            set_value_to_kwargs_param(
                parameter,
                request_value,
                func_kwargs,
                single_field_dict,
                func_sig
            )
        else:
            # support request: Request
            set_value_to_args_param(parameter, dispatch_web, func_args)

    # Support param: type = pait.field.BaseField()
    if single_field_dict:
        func_kwargs.update(single_field_handle(single_field_dict))

    return func_args, func_kwargs
