from typing import Any

from starlette.responses import JSONResponse

from pait.plugin.check_json_resp import AsyncCheckJsonRespPlugin as _AsyncCheckJsonRespPlugin
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AsyncCheckJsonRespPlugin", "CheckJsonRespPlugin"]


class AsyncCheckJsonRespPlugin(JsonProtocol, _AsyncCheckJsonRespPlugin):  # type: ignore
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super().__call__(*args, **kwargs)
        return JSONResponse(response, status_code=self.status_code, headers=self.headers, media_type=self.media_type)


class CheckJsonRespPlugin(JsonProtocol, _CheckJsonRespPlugin):  # type: ignore
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super().__call__(*args, **kwargs)
        return JSONResponse(response, status_code=self.status_code, headers=self.headers, media_type=self.media_type)
