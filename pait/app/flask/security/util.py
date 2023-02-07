from typing import Any, Dict, Optional

from werkzeug.exceptions import HTTPException
from werkzeug.wrappers.response import Response


class HTTPExceptionWithHeaders(HTTPException):
    headers: Optional[dict] = None

    def set_headers(self, headers: Optional[dict] = None) -> None:
        self.headers = headers

    def __call__(self, environ: Any, start_response: Any) -> Response:
        response: Response = self.get_response(environ)
        if self.headers:
            response.headers.update(self.headers)
        return response(environ, start_response)


class GetException(object):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        exc = HTTPExceptionWithHeaders(description=message)
        exc.set_headers(headers)
        exc.code = status_code
        return exc
