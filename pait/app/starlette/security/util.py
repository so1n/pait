from typing import Dict, Optional

from pait.app.starlette import http_exception


class GetException(object):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        return http_exception(status_code=status_code, message=message, headers=headers)
