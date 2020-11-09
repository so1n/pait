import asyncio
import logging
import inspect

from typing import Any, Callable, Coroutine, Dict, List, Mapping, Type, Tuple, Optional, Union, get_type_hints

from pydantic import BaseModel, create_model
from pait import field
from pait.exceptions import (
    NotFoundFieldError,
    NotFoundValueError,
    PaitException,
)
from pait.field import BaseField
from pait.util import FuncSig, PaitModel, get_func_sig
from pait.app.base import (
    BaseAsyncAppDispatch,
    BaseAppDispatch
)


def raise_and_tip(
    parameter: inspect.Parameter,
    _object: Union[FuncSig, Type],
    exception: 'Exception'
):
    param_value: Any = parameter.default
    annotation: Type[BaseModel] = parameter.annotation
    param_name: str = parameter.name

    # Help users quickly locate the error code
    parameter_value_name: str = param_value.__class__.__name__
    param_str: str = (
        f'{param_name}: {annotation} = {parameter_value_name}('
        f'key={param_value.key}, default={param_value.default})'
    )
    if isinstance(_object, FuncSig):
        title: str = 'def'
        if inspect.iscoroutinefunction(_object.func):
            title = 'async def'
        file: str = inspect.getfile(_object.func)
        line: int = inspect.getsourcelines(_object.func)[1]
        error_object_name: str = _object.func.__name__
    else:
        title: str = 'class'
        file: str = inspect.getmodule(_object).__file__
        line: int = inspect.getsourcelines(_object.__class__)[1]
        error_object_name: str = _object.__class__.__name__
    logging.debug(f"""
{title} {error_object_name}(
    ...
    {param_str} <-- error
    ...
):
    pass
            """)
    raise PaitException(
        f'File "{file}",'
        f' line {line},'
        f' in {error_object_name}'
        f' {str(exception)}'
    ) from exception


def single_field_handle(single_field_dict: Dict['inspect.Parameter', Any]) -> BaseModel:
    annotation_dict: Dict[str, Type[Any, ...]] = {}
    param_value_dict: Dict[str, Any] = {}
    for parameter, value in single_field_dict.items():
        annotation_dict[parameter.name] = (parameter.annotation, ...)
        param_value_dict[parameter.name] = value

    dynamic_model: Type[BaseModel] = create_model('DynamicFoobarModel', **annotation_dict)
    return dynamic_model(**param_value_dict)


def get_value_from_request(
    parameter: inspect.Parameter,
    dispatch_web: 'BaseAppDispatch'
) -> Union[Any, Coroutine]:
    # kwargs param
    # support model: pydantic.BaseModel = pait.field.BaseField()
    if isinstance(parameter.default, field.File):
        assert parameter.annotation is not dispatch_web.FileType, f"File type must be {dispatch_web.FileType}"

    field_name: str = parameter.default.__class__.__name__.lower()
    # Note: not use hasattr with LazyProperty (
    #   because hasattr will calling getattr(obj, name) and catching AttributeError,
    # )
    dispatch_web_func:  Union[Callable, Coroutine, None] = getattr(dispatch_web, field_name, None)
    if dispatch_web_func is None:
        raise NotFoundFieldError(f'field: {field_name} not found in {dispatch_web}')
    return dispatch_web_func()


def set_value_to_args_param(
    parameter: inspect.Parameter,
    dispatch_web: 'BaseAppDispatch',
    func_args: list,
):
    # args param
    # Only support request param(def handle(request: Request))
    if parameter.annotation is dispatch_web.RequestType:
        func_args.append(dispatch_web.request_args)
    elif issubclass(parameter.annotation,PaitModel):
        single_field_dict = {}
        _pait_model = parameter.annotation
        for param_name, param_annotation in get_type_hints(_pait_model).items():
            parameter: 'inspect.Parameter' = inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=_pait_model.__field_defaults__[param_name],
                annotation=param_annotation
            )
            request_value: Any = get_value_from_request(parameter, dispatch_web)
            func_kwargs = {}
            set_value_to_kwargs_param(parameter, request_value, func_kwargs, single_field_dict, dispatch_web)
            if func_kwargs:
                raise RuntimeError(
                    f'{PaitModel.__class__.__name__} not support {BaseModel.__class__.__name__} annotation'
                )
        func_args.append(single_field_handle(single_field_dict))
    elif parameter.name == 'self':
        func_args.append(dispatch_web.cbv_class)


async def async_set_value_to_args_param(
    parameter: inspect.Parameter,
    dispatch_web: 'BaseAppDispatch',
    func_args: list,
):
    # args param
    # Only support request param(def handle(request: Request))
    if parameter.annotation is dispatch_web.RequestType:
        func_args.append(dispatch_web.request_args)
    elif issubclass(parameter.annotation, PaitModel):
        single_field_dict = {}
        _pait_model = parameter.annotation
        for param_name, param_annotation in get_type_hints(_pait_model).items():
            parameter: 'inspect.Parameter' = inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=_pait_model.__field_defaults__[param_name],
                annotation=param_annotation
            )
            request_value: Any = get_value_from_request(parameter, dispatch_web)
            if asyncio.iscoroutine(request_value):
                request_value = await request_value

            func_kwargs = {}
            set_value_to_kwargs_param(parameter, request_value, func_kwargs, single_field_dict, dispatch_web)
            if func_kwargs:
                raise RuntimeError(
                    f'{PaitModel.__class__.__name__} not support {BaseModel.__class__.__name__} annotation'
                )
        func_args.append(single_field_handle(single_field_dict))
    elif parameter.name == 'self':
        func_args.append(dispatch_web.cbv_class)


def set_value_to_kwargs_param(
    parameter: inspect.Parameter,
    request_value: Any,
    func_kwargs: Dict[str, Any],
    single_field_dict: Dict['inspect.Parameter', Any],
    dispatch_web: 'BaseAppDispatch',
):
    param_value: BaseField = parameter.default
    annotation: Type[BaseModel] = parameter.annotation
    param_name: str = parameter.name
    if isinstance(request_value, Mapping) or type(request_value) is dispatch_web.HeaderType \
            or type(request_value) is dispatch_web.FormType:
        if param_value.fix_key:
            request_value: Dict[str, Any] = {
                key.lower().replace('-', '_'): value
                for key, value in request_value.items()
            }

        if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            # parse annotation is pydantic.BaseModel
            value: Any = annotation(**request_value)
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
                    parameter_value_name: str = param_value.__class__.__name__
                    param_str: str = (
                        f'{param_name}: {annotation} = {parameter_value_name}('
                        f'key={param_value.key}, default={param_value.default})'
                    )
                    raise NotFoundValueError(
                        f' kwargs param:{param_str} not found in {request_value},'
                        f' try use {parameter_value_name}(key={{key name}})'
                    )
            single_field_dict[parameter] = value
    else:
        single_field_dict[parameter] = request_value


def param_handle(
        dispatch_web: 'BaseAppDispatch',
        _object: Union[FuncSig, Type],
        param_list: List['inspect.Parameter']
) -> Tuple[List[Any], Dict[str, Any]]:
    args_param_list: List[Any] = []
    kwargs_param_dict: Dict[str, Any] = {}
    single_field_dict: Dict['inspect.Parameter', Any] = {}
    for parameter in param_list:
        try:
            if parameter.default != parameter.empty:
                # kwargs param
                # support model: pydantic.BaseModel = pait.field.BaseField()
                if isinstance(parameter.default, field.Depends):
                    func: Callable = parameter.default.func
                    func_sig: FuncSig = get_func_sig(func)
                    _func_args, _func_kwargs = param_handle(dispatch_web, func_sig, func_sig.param_list)
                    func_result: Any = func(*_func_args, **_func_kwargs)
                    kwargs_param_dict[parameter.name] = func_result
                else:
                    request_value: Any = get_value_from_request(parameter, dispatch_web)
                    set_value_to_kwargs_param(
                        parameter,
                        request_value,
                        kwargs_param_dict,
                        single_field_dict,
                        dispatch_web
                    )
            else:
                set_value_to_args_param(parameter, dispatch_web, args_param_list)
        except PaitException as e:
            raise_and_tip(parameter, _object, e)
    # Support param: type = pait.field.BaseField()
    if single_field_dict:
        kwargs_param_dict.update(single_field_handle(single_field_dict).dict())

    return args_param_list, kwargs_param_dict


async def async_param_handle(
        dispatch_web: 'BaseAsyncAppDispatch',
        _object: Union[FuncSig, Type],
        param_list: List['inspect.Parameter']
) -> Tuple[List[Any], Dict[str, Any]]:
    args_param_list: List[Any] = []
    kwargs_param_dict: Dict[str, Any] = {}
    single_field_dict: Dict['inspect.Parameter', Any] = {}
    for parameter in param_list:
        try:
            if parameter.default != parameter.empty:
                # kwargs param
                # support model: pydantic.BaseModel = pait.field.BaseField()
                if isinstance(parameter.default, field.Depends):
                    func: Callable = parameter.default.func
                    func_sig: FuncSig = get_func_sig(func)
                    _func_args, _func_kwargs = await async_param_handle(dispatch_web, func_sig, func_sig.param_list)
                    func_result: Any = func(*_func_args, **_func_kwargs)
                    if asyncio.iscoroutine(func_result):
                        func_result = await func_result
                    kwargs_param_dict[parameter.name] = func_result
                else:
                    request_value: Any = get_value_from_request(parameter, dispatch_web)

                    if asyncio.iscoroutine(request_value):
                        request_value = await request_value

                    set_value_to_kwargs_param(
                        parameter,
                        request_value,
                        kwargs_param_dict,
                        single_field_dict,
                        dispatch_web
                    )
            else:
                # args param
                # support model: model: ModelType
                await async_set_value_to_args_param(parameter, dispatch_web, args_param_list)
        except PaitException as e:
            raise_and_tip(parameter, _object, e)

    # Support param: type = pait.field.BaseField()
    if single_field_dict:
        kwargs_param_dict.update(single_field_handle(single_field_dict).dict())

    return args_param_list, kwargs_param_dict


def get_parameter_list_from_class(cbv_class: Type) -> List['inspect.Parameter']:
    parameter_list: List['inspect.Parameter'] = []
    if not hasattr(cbv_class, '__annotations__'):
        return parameter_list
    for param_name, param_annotation in get_type_hints(cbv_class).items():
        parameter: 'inspect.Parameter' = inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=getattr(cbv_class, param_name),
            annotation=param_annotation)
        parameter_list.append(parameter)
    return parameter_list


async def async_class_param_handle(dispatch_web: 'BaseAsyncAppDispatch'):
    cbv_class: Optional[Type] = dispatch_web.cbv_class
    if not cbv_class:
        return
    param_list: list = get_parameter_list_from_class(cbv_class)
    args, kwargs = await async_param_handle(dispatch_web, cbv_class, param_list)
    cbv_class.__dict__.update(kwargs)


def class_param_handle(dispatch_web: 'BaseAppDispatch'):
    cbv_class: Optional[Type] = dispatch_web.cbv_class
    if not cbv_class:
        return
    param_list: list = get_parameter_list_from_class(cbv_class)
    args, kwargs = param_handle(dispatch_web, cbv_class, param_list)
    cbv_class.__dict__.update(kwargs)


async def async_func_param_handle(
        dispatch_web: 'BaseAsyncAppDispatch',
        func_sig: FuncSig
) -> Tuple[List[Any], Dict[str, Any]]:
    return await async_param_handle(dispatch_web, func_sig, func_sig.param_list)


def func_param_handle(dispatch_web: 'BaseAppDispatch', func_sig: FuncSig) -> Tuple[List[Any], Dict[str, Any]]:
    return param_handle(dispatch_web, func_sig, func_sig.param_list)
