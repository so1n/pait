from typing import Any, Dict, Optional

from tornado.web import RequestHandler

from pait.plugin.base import PluginManager, PluginProtocol


class JsonProtocol(PluginProtocol):
    status: int
    headers: Dict[str, str]
    content_type: str

    def gen_response(self, tornado_handle: RequestHandler, response: Any) -> Any:
        tornado_handle.set_status(self.status)
        if self.headers is not None:
            for k, v in self.headers.items():
                tornado_handle.set_header(k, v)
        tornado_handle.write(response)
        return response

    @classmethod
    def build(  # type: ignore
        cls,
        status: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        **kwargs: Any,
    ) -> "PluginManager":
        return super().build(
            status=status or 200,
            headers=headers or {},
            content_type=content_type or "application/json",
            **kwargs,
        )
