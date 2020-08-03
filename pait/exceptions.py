class PaitException(Exception):
    pass


class FieldKeyError(PaitException):
    pass


class NotFoundFieldError(PaitException):
    pass
