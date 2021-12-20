import inspect
import sys
from dataclasses import dataclass
from typing import Callable, Dict, ForwardRef, List, Optional, Type


@dataclass()
class FuncSig:
    """func inspect.Signature model"""

    func: Callable
    sig: "inspect.Signature"
    param_list: List["inspect.Parameter"]
    cbv_class: Optional[Type] = None


_func_sig_dict: Dict[Callable, FuncSig] = {}


def get_func_sig(func: Callable) -> FuncSig:
    """get func inspect.Signature model"""
    if func in _func_sig_dict:
        return _func_sig_dict[func]

    sig: inspect.Signature = inspect.signature(func)
    param_list: List[inspect.Parameter] = []
    for key in sig.parameters:
        if not (sig.parameters[key].annotation != sig.empty or sig.parameters[key].name == "self"):
            continue
        parameter: inspect.Parameter = sig.parameters[key]
        if isinstance(parameter.annotation, str):
            value: ForwardRef = ForwardRef(parameter.annotation, is_argument=False)
            setattr(
                parameter, "_annotation", value._evaluate(sys.modules[func.__module__].__dict__, None)  # type: ignore
            )
        param_list.append(parameter)

    # return_param = sig.return_annotation
    func_sig: FuncSig = FuncSig(func=func, sig=sig, param_list=param_list)
    _func_sig_dict[func] = func_sig
    return func_sig
