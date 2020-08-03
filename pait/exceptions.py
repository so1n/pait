class PaitException(Exception):
    pass


class NotFoundFieldError(PaitException):
    pass


class NotFoundValueError(PaitException):
    pass
