from typing import Any, Callable, TypeVar

from pait.field.base import BaseField
from pait.types import CallType, ParamSpec

P = ParamSpec("P")
R_T = TypeVar("R_T")


class Depends(BaseField):
    def __init__(self, func: CallType):
        self.func: CallType = func

    @classmethod
    def i(cls, func: CallType) -> Any:
        return cls(func)

    @classmethod
    def t(cls, func: Callable[P, R_T]) -> R_T:  # type: ignore
        return cls(func)  # type: ignore
