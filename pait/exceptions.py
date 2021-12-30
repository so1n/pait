class PaitBaseException(Exception):
    pass


class NotFoundFieldError(PaitBaseException):
    pass


class CheckValueError(PaitBaseException):
    pass
