from typing import Any, Callable, Dict, Optional

from sanic.response import json

from pait.plugin.check_json_resp import AsyncCheckJsonRespPlugin as _AsyncCheckJsonRespPlugin

__all__ = ["AsyncCheckJsonRespPlugin"]


class AsyncCheckJsonRespPlugin(_AsyncCheckJsonRespPlugin):
    def __init__(
        self,
        check_resp_fn: Callable,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "application/json",
        dumps: Optional[Callable[..., str]] = None,
        **json_kwargs: Any,
    ) -> None:
        super(AsyncCheckJsonRespPlugin, self).__init__(check_resp_fn=check_resp_fn)
        self.status: int = status
        self.headers: Optional[Dict[str, str]] = headers
        self.content_type = content_type
        self.dumps: Optional[Callable[..., str]] = dumps
        self.json_kwargs: dict = json_kwargs

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(AsyncCheckJsonRespPlugin, self).__call__(*args, **kwargs)
        return json(
            response,
            status=self.status,
            headers=self.headers,
            content_type=self.content_type,
            dumps=self.dumps,
            **self.json_kwargs,
        )
