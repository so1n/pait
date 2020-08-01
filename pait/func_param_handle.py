import asyncio
import logging
import inspect

from typing import Any, Callable, Coroutine, Dict, List, Type, Tuple, Optional, Union

from pydantic import BaseModel, create_model
from pait import field
from pait.util import FuncSig
from pait.web.base import (
    BaseAsyncWebDispatch,
    BaseWebDispatch
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
    dispatch_web: 'BaseWebDispatch'
) -> Union[Any, Coroutine, None]:
    # kwargs param
    # support model: pydantic.BaseModel = pait.field.BaseField()
    if isinstance(parameter.default, field.File):
        assert parameter.annotation is not dispatch_web.FileType, \
            f"File type must be {dispatch_web.FileType}"
    # Note: not use hasattr with LazyProperty (
    #   because hasattr will calling getattr(obj, name) and catching AttributeError,
    # )
    dispatch_web_func:  Optional[Callable] = getattr(
        dispatch_web, parameter.default.__class__.__name__.lower()
    )
    if not dispatch_web_func:
        return
    return dispatch_web_func()


def set_value_to_kwargs_param(
    parameter: inspect.Parameter,
    request_value,
    func_kwargs,
    single_field_dict,
    _object: Union[FuncSig, Type]
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
                param_str = (
                    f'{param_name}: {annotation} = {parameter_value_name}('
                    f'key={param_value.key}, default={param_value.default})'
                )
                if isinstance(_object, FuncSig):
                    title = 'def'
                    if inspect.iscoroutinefunction(_object.func):
                        title = 'async def'
                    file = inspect.getfile(_object.func)
                    line = inspect.getsourcelines(_object.__class__)[1] + 1
                    error_object_name = _object.func.__name__
                else:
                    title = 'class'
                    file = inspect.getmodule(_object).__file__
                    line = inspect.getsourcelines(_object.__class__)[1]
                    error_object_name = _object.__class__.__name__
                logging.debug(f"""
    {title} {error_object_name}(
        ...
        {param_str} <-- error
        ...
    ):
        pass
                                  """)

                raise KeyError(
                    f'File "{file}",'
                    f' line {line},'
                    f' in {error_object_name}\n'
                    f' kwargs param:{param_str} not found value,'
                    f' try use {parameter_value_name}(key={{key name}})'
                )
        single_field_dict[parameter] = value


async def async_class_param_handle(dispatch_web: 'BaseAsyncWebDispatch'):
    cbv_class: Optional[Type] = dispatch_web.cbv_class
    single_field_dict: Dict['inspect.Parameter', Any] = {}
    if not cbv_class:
        return
    for param_name, param_annotation in cbv_class.__annotations__.items():
        parameter: 'inspect.Parameter' = inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=getattr(cbv_class, param_name),
            annotation=param_annotation)
        request_value = extract_request_kwargs_data(parameter, dispatch_web)
        if asyncio.iscoroutine(request_value):
            request_value = await request_value
        set_value_to_kwargs_param(
            parameter,
            request_value,
            cbv_class.__dict__,
            single_field_dict,
            cbv_class
        )
    if single_field_dict:
        cbv_class.__dict__.update(single_field_handle(single_field_dict))
    return


async def async_func_param_handle(dispatch_web: 'BaseAsyncWebDispatch', func_sig: FuncSig) -> Tuple[List, Dict]:
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

    # Support param: type = pait.field.BaseField()
    if single_field_dict:
        func_kwargs.update(single_field_handle(single_field_dict))

    return func_args, func_kwargs


def func_param_handle(dispatch_web: 'BaseWebDispatch', func_sig: FuncSig) -> Tuple[List, Dict]:
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

    # Support param: type = pait.field.BaseField()
    if single_field_dict:
        func_kwargs.update(single_field_handle(single_field_dict))

    return func_args, func_kwargs
