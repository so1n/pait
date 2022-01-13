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


class NotFoundFieldError(PaitBaseParamException):
    pass


class FieldValueTypeError(PaitBaseParamException):
    pass
