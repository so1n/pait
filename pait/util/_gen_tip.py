import inspect
import logging
from typing import Any, Optional, Type

from pydantic import BaseModel

from pait.exceptions import TipException
from pait.field import BaseRequestResourceField

_indent: str = 4 * " "

__all__ = ["gen_tip_exc"]


def gen_tip_exc(
    _object: Any,
    exception: "Exception",
    parameter: Optional[inspect.Parameter] = None,
    tip_exception_class: Optional[Type[TipException]] = TipException,
) -> Exception:
    """Help users understand which parameter is wrong"""
    if _object is None or tip_exception_class is None or isinstance(exception, TipException):
        return exception

    if parameter:
        param_value: BaseRequestResourceField = parameter.default
        annotation: Type[BaseModel] = parameter.annotation
        param_name: str = parameter.name

        parameter_value_name: str = param_value.__class__.__name__
        if param_value is parameter.empty:
            param_str: str = f"{param_name}: {annotation}"
        else:
            param_str = f"{param_name}: {annotation} = {parameter_value_name}"
            if isinstance(param_value, BaseRequestResourceField):
                param_str += f"({param_value})"
    else:
        param_str = ""

    file: Optional[str] = None
    if inspect.isfunction(_object):
        title: str = "def"
        if inspect.iscoroutinefunction(_object):
            title = "async def"
        file = inspect.getfile(_object)
        line: int = inspect.getsourcelines(_object)[1]
        error_object_name: str = _object.__name__
        error_source_tip: str = (
            f"{title} {error_object_name}(\n"
            f"{_indent}...\n"
            f"{_indent}{param_str} <-- error\n"
            f"{_indent}...\n):\n"
            f"{_indent}pass"
        )
    else:
        module: Any = inspect.getmodule(_object)
        if module:
            file = module.__file__

        class_object = _object.__class__ if not inspect.isclass(_object) else _object
        line = inspect.getsourcelines(class_object)[1]
        error_object_name = class_object.__name__
        if "class" in error_object_name:
            error_object_name = str(class_object)  # pragma: no cover
        error_source_tip = f"class: `{error_object_name}`  attributes error\n    {param_str}"

    logging.debug(error_source_tip)
    exc_msg: str = (
        f"{str(exception)} for {_object}   Customer Traceback:\n"
        f'{_indent}File "{file}",'
        f" line {line},"
        f" in {error_object_name}."
    )
    return tip_exception_class(exc_msg, exception)
