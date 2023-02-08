from typing import Dict, Optional

from tornado.web import HTTPError

from pait.app.base.security.api_key import BaseAPIKey


class APIKey(BaseAPIKey):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        # tornado not support read header from exc
        return HTTPError(status_code=status_code, reason=message)
