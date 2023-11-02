import json
from typing import Any

from tornado.web import RequestHandler

from pait.model.context import ContextModel as PluginContext
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

__all__ = ["CheckJsonRespPlugin"]


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    json_media_type: str = "application/json; charset=UTF-8"

    @classmethod
    def get_json(cls, response_data: Any, context: PluginContext) -> dict:
        if response_data is None:
            tornado_handle: RequestHandler = context.args[0]
            content_type_list = tornado_handle._headers.get_list("Content-Type")
            if cls.json_media_type in content_type_list:
                return json.loads(tornado_handle._write_buffer[-1].decode())
            else:
                raise ValueError(f"Expected '{cls.json_media_type}', but got '{content_type_list}'")  # pragma: no cover
        else:
            raise TypeError(f"Expected type must None but got type {type(response_data)}")  # pragma: no cover

    async def _async_call(self, context: PluginContext) -> Any:
        try:
            return await super()._async_call(context)
        except Exception:
            tornado_handle: RequestHandler = context.args[0]
            tornado_handle.clear()
            raise
