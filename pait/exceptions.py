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
