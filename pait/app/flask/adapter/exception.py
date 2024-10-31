from typing import TYPE_CHECKING, Any, Iterable, Optional, cast

from werkzeug.exceptions import HTTPException

if TYPE_CHECKING:
    from .wrappers.response import Response as WSGIResponse  # noqa: F401


class HTTPExceptionWithHeaders(HTTPException):
    headers: Optional[dict] = None

    def set_headers(self, headers: Optional[dict] = None) -> None:
        self.headers = headers

    def __call__(self, environ: Any, start_response: Any) -> Iterable[bytes]:
        response = cast("WSGIResponse", self.get_response(environ))
        if self.headers:
            response.headers.update(self.headers)
        return response(environ, start_response)


def http_exception(*, status_code: int, message: str, headers: Optional[dict] = None) -> Exception:
    exc = HTTPExceptionWithHeaders(description=message)
    exc.set_headers(headers)
    exc.code = status_code
    return exc
