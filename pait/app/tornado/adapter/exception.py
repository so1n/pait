from typing import Optional

from tornado.web import HTTPError


def http_exception(*, status_code: int, message: str, headers: Optional[dict] = None) -> Exception:
    exc: HTTPError = HTTPError(reason=message, status_code=status_code)
    if headers:
        exc.headers = headers
    return exc
