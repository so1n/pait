import inspect
import logging
from typing import Any, Optional, Type

from pydantic import BaseModel

from pait.exceptions import TipException
from pait.field import BaseField
from pait.util import FuncSig


def gen_tip_exc(_object: Any, exception: "Exception", parameter: Optional[inspect.Parameter] = None) -> Exception:
    """Help users understand which parameter is wrong"""
    if not parameter and (getattr(exception, "_is_tip_exc", None) or isinstance(exception, TipException)):
        return exception
    if parameter:
        param_value: BaseField = parameter.default
        annotation: Type[BaseModel] = parameter.annotation
        param_name: str = parameter.name

        parameter_value_name: str = param_value.__class__.__name__
        if param_value is parameter.empty:
            param_str: str = f"{param_name}: {annotation}"
        else:
            param_str = f"{param_name}: {annotation} = {parameter_value_name}"
            if isinstance(param_value, BaseField):
                param_str += f"(alias={param_value.alias}, default={param_value.default})"
    else:
        param_str = ""

    file: Optional[str] = None
    if isinstance(_object, FuncSig):
        _object = _object.func
    if inspect.isfunction(_object):
        title: str = "def"
        if inspect.iscoroutinefunction(_object):
            title = "async def"
        file = inspect.getfile(_object)
        line: int = inspect.getsourcelines(_object)[1]
        error_object_name: str = _object.__name__
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
    else:
        module: Any = inspect.getmodule(_object)
        if module:
            file = module.__file__
        line = inspect.getsourcelines(_object.__class__)[1]
        error_object_name = _object.__class__.__name__
        if "class" in error_object_name:
            error_object_name = str(_object.__class__)  # pragma: no cover
        logging.debug(f"class: `{error_object_name}`  attributes error\n    {param_str}")

    setattr(exception, "_is_tip_exc", True)
    exc_msg: str = f'File "{file}",' f" line {line}," f" in {error_object_name}." f"\nerror:{str(exception)}"
    return TipException(exc_msg, exception)
