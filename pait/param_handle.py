import asyncio
import inspect
import logging
from typing import Any, Callable, Coroutine, Dict, List, NoReturn, Mapping, Optional, Tuple, Type, Union, get_type_hints
from types import ModuleType

from pydantic import BaseModel, create_model

from pait import field
from pait.app.base import BaseAppHelper, BaseAsyncAppHelper
from pait.exceptions import NotFoundFieldError, NotFoundValueError, PaitBaseException
from pait.field import BaseField
from pait.model import FuncSig, PaitBaseModel
from pait.util import get_func_sig, get_parameter_list_from_class


def raise_and_tip(
        _object: Union[FuncSig, Type], exception: "Exception", parameter: Optional[inspect.Parameter] = None
) -> NoReturn:
    """Help users understand which parameter is wrong"""
    if parameter:
        param_value: BaseField = parameter.default
        annotation: Type[BaseModel] = parameter.annotation
        param_name: str = parameter.name

        parameter_value_name: str = param_value.__class__.__name__
        if param_value is parameter.empty:
            param_str: str = f"{param_name}: {annotation}"
        else:
            param_str = (
                f"{param_name}: {annotation} = {parameter_value_name}"
                f"(alias={param_value.alias}, default={param_value.default})"
            )
    else:
        param_str = ""

    file: Optional[str] = None
    if isinstance(_object, FuncSig):
        title: str = "def"
        if inspect.iscoroutinefunction(_object.func):
            title = "async def"
        file = inspect.getfile(_object.func)
        line: int = inspect.getsourcelines(_object.func)[1]
        error_object_name: str = _object.func.__name__
    else:
        title = "class"
        module: Optional[ModuleType] = inspect.getmodule(_object)
        if module:
            file = module.__file__
        line = inspect.getsourcelines(_object.__class__)[1]
        error_object_name = _object.__class__.__name__
    logging.debug(
        f"""
{title} {error_object_name}(
    ...
    {param_str} <-- error
    ...
):
    pass
"""
    )
    raise PaitBaseException(
        f'File "{file}",' f" line {line}," f" in {error_object_name}." f" error:{str(exception)}"
    ) from exception


def parameter_2_basemodel(parameter_value_dict: Dict["inspect.Parameter", Any]) -> BaseModel:
    """Convert all parameters into pydantic mods"""
    annotation_dict: Dict[str, Tuple[Type, Any]] = {}
    param_value_dict: Dict[str, Any] = {}
    for parameter, value in parameter_value_dict.items():
        annotation_dict[parameter.name] = (parameter.annotation, ...)
        param_value_dict[parameter.name] = value

    dynamic_model: Type[BaseModel] = create_model("DynamicFoobarModel", **annotation_dict)
    return dynamic_model(**param_value_dict)


def get_request_value_from_parameter(
    parameter: inspect.Parameter, app_helper: "BaseAppHelper"
) -> Union[Any, Coroutine]:
    if isinstance(parameter.default, field.File):
        assert parameter.annotation is not app_helper.FileType, f"File type must be {app_helper.FileType}"

    field_name: str = parameter.default.__class__.__name__.lower()
    # Note: not use hasattr with LazyProperty (
    #   because hasattr will calling getattr(obj, name) and catching AttributeError,
    # )
    app_field_func: Optional[Callable] = getattr(app_helper, field_name, None)
    if app_field_func is None:
        raise NotFoundFieldError(f"field: {field_name} not found in {app_helper}")
    return app_field_func()


def set_parameter_value_to_args_list(
        parameter: inspect.Parameter, app_helper: "BaseAppHelper", func_args: list
) -> None:
    """use func_args param faster return and extend func_args"""
    if parameter.name == "self" and not func_args:
        # Only support self param name
        func_args.append(app_helper.cbv_class)
    elif parameter.annotation is app_helper.RequestType:
        # support request param(def handle(request: Request))
        func_args.append(app_helper.request_args)
    elif issubclass(parameter.annotation, PaitBaseModel):
        # support pait_model param(def handle(model: PaitBaseModel))
        single_field_dict: Dict["inspect.Parameter", Any] = {}
        _pait_model: Type[PaitBaseModel] = parameter.annotation
        for param_name, param_annotation in get_type_hints(_pait_model).items():
            if param_name.startswith("_"):
                continue
            parameter = inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=getattr(_pait_model, param_name),
                annotation=param_annotation,
            )
            request_value: Any = get_request_value_from_parameter(parameter, app_helper)
            # PaitModel's attributes's annotation support BaseModel
            request_value_handle(parameter, request_value, None, single_field_dict, app_helper)
        func_args.append(parameter_2_basemodel(single_field_dict))


async def async_set_value_to_args_param(
    parameter: inspect.Parameter, dispatch_app: "BaseAppHelper", func_args: list
) -> None:
    """use func_args param faster return and extend func_args"""
    # args param
    if parameter.name == "self":
        # Only support self param name
        func_args.append(dispatch_app.cbv_class)
    elif parameter.annotation is dispatch_app.RequestType:
        # support request param(def handle(request: Request))
        func_args.append(dispatch_app.request_args)
    elif issubclass(parameter.annotation, PaitBaseModel):
        # support pait_model param(def handle(model: PaitModel))
        single_field_dict: Dict["inspect.Parameter", Any] = {}
        _pait_model: Type[PaitBaseModel] = parameter.annotation

        for param_name, param_annotation in get_type_hints(_pait_model).items():
            if param_name.startswith("_"):
                continue
            parameter = inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=getattr(_pait_model, param_name),
                annotation=param_annotation,
            )
            request_value: Any = get_request_value_from_parameter(parameter, dispatch_app)
            if asyncio.iscoroutine(request_value):
                request_value = await request_value
            # PaitModel's attributes  support BaseModel
            request_value_handle(parameter, request_value, None, single_field_dict, dispatch_app)
        func_args.append(parameter_2_basemodel(single_field_dict))


def request_value_handle(
    parameter: inspect.Parameter,
    request_value: Any,
    base_model_dict: Optional[Dict[str, Any]],
    parameter_value_dict: Dict["inspect.Parameter", Any],
    app_helper: "BaseAppHelper",
) -> None:
    """parse request_value and set to base_model_dict or parameter_value_dict"""
    param_value: BaseField = parameter.default
    annotation: Type[BaseModel] = parameter.annotation
    param_name: str = parameter.name
    if (
        isinstance(request_value, Mapping)
        or type(request_value) is app_helper.HeaderType
        or type(request_value) is app_helper.FormType
    ):
        if not isinstance(param_value, BaseField):
            raise PaitBaseException(f"must use {BaseField.__class__.__name__}, no {param_value}")

        if base_model_dict is not None and inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            # parse annotation is pydantic.BaseModel and base_model_dict not None
            value: Any = annotation(**request_value)
            base_model_dict[parameter.name] = value
        else:
            # parse annotation is python type and pydantic.field
            if type(param_value.alias) is str and param_value.alias in request_value:
                value = request_value.get(param_value.alias, param_value.default)
            elif param_name in request_value:
                value = request_value.get(param_name, param_value.default)
            else:
                if param_value.default:
                    value = param_value.default
                else:
                    parameter_value_name: str = param_value.__class__.__name__
                    param_str: str = (
                        f"{param_name}: {annotation} = {parameter_value_name}("
                        f"alias={param_value.alias}, default={param_value.default})"
                    )
                    raise NotFoundValueError(
                        f" kwargs param:{param_str} not found in {request_value},"
                        f" try use {parameter_value_name}(alias={{alias}})"
                    )
            parameter_value_dict[parameter] = value
    else:
        parameter_value_dict[parameter] = request_value


def param_handle(
    app_helper: "BaseAppHelper", _object: Union[FuncSig, Type], param_list: List["inspect.Parameter"]
) -> Tuple[List[Any], Dict[str, Any]]:
    args_param_list: List[Any] = []
    kwargs_param_dict: Dict[str, Any] = {}
    single_field_dict: Dict["inspect.Parameter", Any] = {}

    for parameter in param_list:
        try:
            if parameter.default != parameter.empty:
                # kwargs param
                # support model: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseField())
                if isinstance(parameter.default, field.Depends):
                    func: Callable = parameter.default.func
                    func_sig: FuncSig = get_func_sig(func)
                    _func_args, _func_kwargs = param_handle(app_helper, func_sig, func_sig.param_list)
                    func_result: Any = func(*_func_args, **_func_kwargs)
                    kwargs_param_dict[parameter.name] = func_result
                else:
                    request_value: Any = get_request_value_from_parameter(parameter, app_helper)
                    request_value_handle(parameter, request_value, kwargs_param_dict, single_field_dict, app_helper)
            else:
                # args param
                # support model: model: ModelType
                set_parameter_value_to_args_list(parameter, app_helper, args_param_list)
        except PaitBaseException as e:
            raise_and_tip(_object, e, parameter)
    # support field: def demo(demo_param: int = pait.field.BaseField())
    if single_field_dict:
        try:
            kwargs_param_dict.update(parameter_2_basemodel(single_field_dict).dict())
        except Exception as e:
            raise_and_tip(_object, e)
    return args_param_list, kwargs_param_dict


async def async_param_handle(
    dispatch_web: "BaseAsyncAppHelper", _object: Union[FuncSig, Type], param_list: List["inspect.Parameter"]
) -> Tuple[List[Any], Dict[str, Any]]:
    args_param_list: List[Any] = []
    kwargs_param_dict: Dict[str, Any] = {}
    single_field_dict: Dict["inspect.Parameter", Any] = {}
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
                    request_value: Any = get_request_value_from_parameter(parameter, dispatch_web)

                    if asyncio.iscoroutine(request_value) or asyncio.isfuture(request_value):
                        request_value = await request_value

                    request_value_handle(parameter, request_value, kwargs_param_dict, single_field_dict, dispatch_web)
            else:
                # args param
                # support model: model: ModelType
                await async_set_value_to_args_param(parameter, dispatch_web, args_param_list)
        except PaitBaseException as e:
            raise_and_tip(_object, e, parameter)

    # support field: def demo(demo_param: int = pait.field.BaseField())
    if single_field_dict:
        try:
            kwargs_param_dict.update(parameter_2_basemodel(single_field_dict).dict())
        except Exception as e:
            raise_and_tip(_object, e)
    return args_param_list, kwargs_param_dict


async def async_class_param_handle(dispatch_web: "BaseAsyncAppHelper") -> None:
    cbv_class: Optional[Type] = dispatch_web.cbv_class
    if not cbv_class:
        return
    param_list: list = get_parameter_list_from_class(cbv_class)
    args, kwargs = await async_param_handle(dispatch_web, cbv_class, param_list)
    cbv_class.__dict__.update(kwargs)


def class_param_handle(dispatch_web: "BaseAppHelper") -> None:
    cbv_class: Optional[Type] = dispatch_web.cbv_class
    if not cbv_class:
        return
    param_list: list = get_parameter_list_from_class(cbv_class)
    args, kwargs = param_handle(dispatch_web, cbv_class, param_list)
    cbv_class.__dict__.update(kwargs)


async def async_func_param_handle(
    dispatch_app: "BaseAsyncAppHelper", func_sig: FuncSig
) -> Tuple[List[Any], Dict[str, Any]]:
    return await async_param_handle(dispatch_app, func_sig, func_sig.param_list)


def func_param_handle(dispatch_app: "BaseAppHelper", func_sig: FuncSig) -> Tuple[List[Any], Dict[str, Any]]:
    return param_handle(dispatch_app, func_sig, func_sig.param_list)
