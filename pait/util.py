import inspect

from dataclasses import dataclass
from typing import Callable, List


@dataclass()
class FuncSig:
    func: Callable
    sig: 'inspect.Signature'
    param_list: List['inspect.Parameter']


def get_func_sig(func: Callable) -> FuncSig:
    sig: 'inspect.signature' = inspect.signature(func)
    param_list: List[inspect.Parameter] = [
        sig.parameters[key]
        for key in sig.parameters
        if sig.parameters[key].annotation != sig.empty
    ]
    # return_param = sig.return_annotation
    return FuncSig(
        func=func,
        sig=sig,
        param_list=param_list,
    )

