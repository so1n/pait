from typing import Any, Callable, Dict, Optional

from sanic import HTTPResponse
from sanic.response import json

from pait.plugin.base import PluginManager, PluginProtocol


class JsonProtocol(PluginProtocol):
    status: int
    headers: Optional[Dict[str, str]]
    content_type: str
    dumps: Optional[Callable[..., str]]
    json_kwargs: dict

    def gen_response(self, response: Any) -> HTTPResponse:
        return json(
            response,
            status=self.status,
            headers=self.headers,
            content_type=self.content_type,
            dumps=self.dumps,
            **self.json_kwargs if self.json_kwargs else {},
        )

    @classmethod
    def build(
        cls,
        status: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        dumps: Optional[Callable[..., str]] = None,
        json_kwargs: Optional[dict] = None,
        **kwargs: Any,
    ) -> "PluginManager":
        return super().build(
            status=status or 200,
            headers=headers or {},
            content_type=content_type or "application/json",
            dumps=dumps,
            json_kwargs=json_kwargs,
            **kwargs,
        )
