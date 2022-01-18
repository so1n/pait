from typing import Any, Callable, Optional

from starlette.responses import JSONResponse

from pait.plugin.check_json_resp import AsyncCheckJsonRespPlugin as _AsyncCheckJsonRespPlugin
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

__all__ = ["AsyncCheckJsonRespPlugin", "CheckJsonRespPlugin"]


class AsyncCheckJsonRespPlugin(_AsyncCheckJsonRespPlugin):
    def __init__(
        self,
        check_resp_fn: Callable,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
    ) -> None:
        super(AsyncCheckJsonRespPlugin, self).__init__(check_resp_fn=check_resp_fn)
        self.status_code: int = status_code
        self.headers: Optional[dict] = headers
        self.media_type: Optional[str] = media_type

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super().__call__(*args, **kwargs)
        return JSONResponse(response, status_code=self.status_code, headers=self.headers, media_type=self.media_type)


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    def __init__(
        self,
        check_resp_fn: Callable,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
    ) -> None:
        super(CheckJsonRespPlugin, self).__init__(check_resp_fn=check_resp_fn)
        self.status_code: int = status_code
        self.headers: Optional[dict] = headers
        self.media_type: Optional[str] = media_type

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super().__call__(*args, **kwargs)
        return JSONResponse(response, status_code=self.status_code, headers=self.headers, media_type=self.media_type)
