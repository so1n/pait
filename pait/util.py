import inspect
from abc import ABC

from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Optional


@dataclass()
class FuncSig:
    sig: 'inspect.Signature'
    param_list: List['inspect.Parameter']


class BaseHelper(object):
    RequestType: Optional[Any] = None
    FormType: Optional[Any] = None
    FileType: Optional[Any] = None

    def __init__(self, request: Any):
        self.request: Any = request

    def body(self) -> dict:
        raise NotImplementedError

    def cookie(self, key: str) -> str:
        raise NotImplementedError

    def file(self):
        raise NotImplementedError

    def from_(self):
        raise NotImplementedError

    def header(self, header_key: str) -> str:
        raise NotImplementedError

    def query(self) -> dict:
        raise NotImplementedError


class BaseAsyncHelper(BaseHelper, ABC):

    def __init__(self, request: Any):
        super().__init__(request)

    async def body(self) -> dict:
        raise NotImplementedError

    async def file(self):
        raise NotImplementedError

    async def from_(self) -> Mapping:
        raise NotImplementedError


def get_func_sig(func: Callable) -> FuncSig:
    sig: 'inspect.signature' = inspect.signature(func)
    param_list: List[inspect.Parameter] = [
        sig.parameters[key]
        for key in sig.parameters
        if sig.parameters[key].annotation != sig.empty
    ]
    # return_param = sig.return_annotation
    return FuncSig(sig=sig, param_list=param_list)

