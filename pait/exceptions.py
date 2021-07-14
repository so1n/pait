class PaitBaseException(Exception):
    pass


class NotFoundFieldError(PaitBaseException):
    pass


class NotFoundValueError(PaitBaseException):
    pass


class CheckValueError(PaitBaseException):
    pass
