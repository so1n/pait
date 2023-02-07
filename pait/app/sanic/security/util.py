from typing import Dict, Optional

from sanic.exceptions import SanicException


class GetException(object):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        exc: SanicException = SanicException(message=message, status_code=status_code)
        if headers:
            exc.headers = headers
        return exc
