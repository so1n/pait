from typing import Dict, Optional

from starlette.exceptions import HTTPException


class GetException(object):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        exc: HTTPException = HTTPException(detail=message, status_code=status_code)
        if headers:
            exc.headers = headers
        return exc
