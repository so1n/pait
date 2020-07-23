import inspect

from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, create_model
from pait import field
from pait.util import (
    BaseAsyncHelper,
    BaseHelper,
    FuncSig
)


def single_field_handle(single_field_dict: Dict['inspect.Parameter', Any]) -> dict:
    annotation_dict = {}
    param_value_dict = {}
    for parameter, value in single_field_dict.items():
        annotation_dict[parameter.name] = (parameter.annotation, ...)
        param_value_dict[parameter.name] = value

    dynamic_model = create_model('DynamicFoobarModel', **annotation_dict)
    return dynamic_model(**param_value_dict).dict()


def func_param_handle(dispatch_web: 'BaseHelper', func_sig: FuncSig) -> Tuple[List, Dict]:
    func_args = []
    func_kwargs = {}
    single_field_dict: Dict['inspect.Parameter', Any] = {}
    for parameter in func_sig.param_list:
        parameter_value = parameter.default
        annotation = parameter.annotation
        if parameter_value != func_sig.sig.empty:
            # kwargs param
            # support model: pydantic.BaseModel = pait.field.BaseField()

            # if isinstance(parameter_value, field.File):
            #     assert parameter.annotation is not dispatch_web.FileType, \
            #         f"File type must be {dispatch_web.FileType}"
            # parameter_value_obj_name = parameter_value.__class__.__name__.lower().strip()
            # if hasattr(dispatch_web, parameter_value_obj_name):
            #     value = getattr(dispatch_web, parameter_value_obj_name)
            # else:
            #     continue
            if isinstance(parameter_value, field.Query):
                value = dispatch_web.query()
            elif isinstance(parameter_value, field.Body):
                value = dispatch_web.body()
            elif isinstance(parameter_value, field.Header):
                value = dispatch_web.header(parameter_value.header_key)
            elif isinstance(parameter_value, field.File):
                assert parameter.annotation is not dispatch_web.FileType,\
                    f"File type must be {dispatch_web.FileType}"
                value = dispatch_web.file()
            elif isinstance(parameter_value, field.From):
                value = dispatch_web.from_()
            else:
                continue

            if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                value = parameter.annotation(**value)
            else:
                single_field_dict[parameter] = value.get(parameter.name, parameter_value.default)
                continue

            func_kwargs[parameter.name] = value
        else:
            # args param
            # Only support request param(def handle(request: Request))
            if parameter.annotation is dispatch_web.RequestType:
                value = dispatch_web.request
                func_args.append(value)
                # Now Not Support other args

    # Support param: type = pait.field.BaseField()
    if single_field_dict:
        func_kwargs.update(single_field_handle(single_field_dict))

    return func_args, func_kwargs


async def async_func_param_handle(dispatch_web: 'BaseAsyncHelper', func_sig: FuncSig) -> Tuple[List, Dict]:
    func_args = []
    func_kwargs = {}
    single_field_dict: Dict['inspect.Parameter', Any] = {}
    for parameter in func_sig.param_list:
        parameter_value = parameter.default
        annotation = parameter.annotation
        if parameter_value != func_sig.sig.empty:
            # kwargs param
            # support model: pydantic.BaseModel = pait.field.BaseField()
            if isinstance(parameter_value, field.Query):
                value = dispatch_web.query()
            elif isinstance(parameter_value, field.Body):
                value = await dispatch_web.body()
            elif isinstance(parameter_value, field.Header):
                value = dispatch_web.header(parameter_value.header_key)
            elif isinstance(parameter_value, field.File):
                assert parameter.annotation is not dispatch_web.FileType,\
                    f"File type must be {dispatch_web.FileType}"
                value = await dispatch_web.file()
            elif isinstance(parameter_value, field.From):
                value = await dispatch_web.from_()
            else:
                continue

            if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                value = parameter.annotation(**value)
            else:
                single_field_dict[parameter] = value.get(parameter.name, parameter_value.default)
                continue

            func_kwargs[parameter.name] = value
        else:
            # args param
            # Only support request param(def handle(request: Request))
            if parameter.annotation is dispatch_web.RequestType:
                value = dispatch_web.request
                func_args.append(value)
                # Now Not Support other args

    # Support param: type = pait.field.BaseField()
    if single_field_dict:
        func_kwargs.update(single_field_handle(single_field_dict))

    return func_args, func_kwargs
