from typing import Optional

from sanic.exceptions import SanicException


def http_exception(*, status_code: int, message: str, headers: Optional[dict] = None) -> Exception:
    exc: SanicException = SanicException(message=message, status_code=status_code)
    if headers:
        exc.headers = headers
    return exc
