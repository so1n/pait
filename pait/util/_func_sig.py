import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type

from typing_extensions import Self  # type: ignore

from ._util import get_real_annotation

__all__ = ["FuncSig", "get_func_sig", "is_bounded_func", "get_pait_handler"]

from ..types import CallType


@dataclass()
class FuncSig:
    """func inspect.Signature model"""

    func: CallType
    sig: "inspect.Signature"
    param_list: List["inspect.Parameter"]
    return_param: Any
    cbv_class: Optional[Type] = None


_func_sig_dict: Dict[CallType, FuncSig] = {}


def get_pait_handler(func: CallType) -> Callable:
    # support pait handler
    if hasattr(func, "pait_handler"):
        pait_handler = getattr(func, "pait_handler")
    elif inspect.isclass(func) and hasattr(func, "__call__"):
        pait_handler = getattr(func, "__call__")
    else:
        pait_handler = func
    return pait_handler


def get_func_sig(func: CallType, cache_sig: bool = True) -> FuncSig:
    """get func inspect.Signature model"""
    if func in _func_sig_dict:
        return _func_sig_dict[func]

    # support pait handler
    pait_handler = get_pait_handler(func)

    sig = inspect.signature(pait_handler)
    param_list: List[inspect.Parameter] = []
    for key in sig.parameters:
        # NOTE:
        #   The cbv func decorated in Pait is unbound, so it can get to self；
        #   Depend func must be bound func when it is used, so it cannot get self；
        if not (sig.parameters[key].annotation != sig.empty or sig.parameters[key].name == "self"):
            if sig.parameters[key].annotation != Self:
                # If the name of the self variable is not self and the annotation is not Self,
                # it will be ignored directly
                continue
        parameter: inspect.Parameter = sig.parameters[key]
        setattr(parameter, "_annotation", get_real_annotation(parameter.annotation, pait_handler))
        param_list.append(parameter)

    func_sig: FuncSig = FuncSig(
        func=pait_handler,
        sig=sig,
        param_list=param_list,
        return_param=get_real_annotation(sig.return_annotation, pait_handler),
    )
    if cache_sig:
        _func_sig_dict[func] = func_sig
    return func_sig


def is_bounded_func(func: Callable) -> bool:
    return inspect.signature(func).parameters.get("self", None) is None
