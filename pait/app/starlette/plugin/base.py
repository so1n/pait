from typing import Any, Optional

from starlette.responses import JSONResponse

from pait.plugin.base import PluginManager, PluginProtocol


class JsonProtocol(PluginProtocol):
    status_code: int
    headers: Optional[dict]
    media_type: Optional[str]

    def gen_response(self, response: Any) -> JSONResponse:
        return JSONResponse(response, status_code=self.status_code, headers=self.headers, media_type=self.media_type)

    @classmethod
    def build(  # type: ignore
        cls,
        status_code: Optional[int] = None,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        **kwargs: Any,
    ) -> "PluginManager":
        return super().build(
            status_code=status_code or 200,
            headers=headers or {},
            media_type=media_type,
            **kwargs,
        )
