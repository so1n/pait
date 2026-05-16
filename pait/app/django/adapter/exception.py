from typing import Optional


class DjangoHTTPException(Exception):
    def __init__(self, *, status_code: int, message: str, headers: Optional[dict] = None):
        self.status_code = status_code
        self.message = message
        self.headers = headers or {}
        super().__init__(message)


def http_exception(*, status_code: int, message: str, headers: Optional[dict] = None) -> Exception:
    return DjangoHTTPException(status_code=status_code, message=message, headers=headers)
