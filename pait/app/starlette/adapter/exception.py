from typing import Optional

from starlette.exceptions import HTTPException


def http_exception(*, status_code: int, message: str, headers: Optional[dict] = None) -> Exception:
    exc: HTTPException = HTTPException(detail=message, status_code=status_code)
    if headers:
        exc.headers = headers
    return exc
