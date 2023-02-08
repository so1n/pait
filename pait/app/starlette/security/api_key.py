from typing import Dict, Optional

from starlette.exceptions import HTTPException

from pait.app.base.security.api_key import BaseAPIKey


class APIKey(BaseAPIKey):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        # starlette not support read header from exc
        return HTTPException(status_code=status_code, detail=message)
