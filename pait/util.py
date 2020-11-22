import inspect

from typing import Callable, List, Type, get_type_hints

from pait.model import FuncSig


class UndefinedType:
    def __repr__(self) -> str:
        return 'PaitUndefined'


Undefined: UndefinedType = UndefinedType()


def get_func_sig(func: Callable) -> FuncSig:
    sig: 'inspect.signature' = inspect.signature(func)
    param_list: List[inspect.Parameter] = [
        sig.parameters[key]
        for key in sig.parameters
        if sig.parameters[key].annotation != sig.empty or sig.parameters[key].name == 'self'
    ]
    # return_param = sig.return_annotation
    return FuncSig(func=func, sig=sig, param_list=param_list)


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