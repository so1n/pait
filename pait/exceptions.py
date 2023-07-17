from typing import Any, List, Optional, Sequence, Type

from pydantic import BaseModel


class PaitBaseException(Exception):
    pass


class CheckValueError(PaitBaseException):
    pass


class ParseTypeError(PaitBaseException):
    pass


class PaitBaseParamException(PaitBaseException):
    def __init__(self, param: str, msg: str):
        super().__init__(msg)
        self.param: str = param
        self.msg: str = msg


class NotFoundFieldException(PaitBaseParamException):
    pass


class NotFoundValueException(PaitBaseParamException):
    pass


class FieldValueTypeException(PaitBaseParamException):
    pass


class TipException(PaitBaseException):
    def __init__(self, msg: str, exc: Exception):
        super().__init__(msg)
        self.exc: Exception = exc


class ValidationError(ValueError):
    __slots__ = "raw_errors", "model", "_error_cache"

    def __init__(self, errors: Sequence[Any], model: "Type[BaseModel]") -> None:
        self._error = errors
        self.model = model
        self._error_cache: Optional[List[dict]] = None

    def errors(self) -> Sequence[Any]:
        return self._error
