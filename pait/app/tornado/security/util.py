from typing import Dict, Optional

from tornado.web import HTTPError


class GetException(object):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        exc: HTTPError = HTTPError(reason=message, status_code=status_code)
        if headers:
            exc.headers = headers
        return exc
