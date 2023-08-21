import json
from typing import Any

from starlette.responses import Response

from pait.model.context import ContextModel as PluginContext
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

__all__ = ["CheckJsonRespPlugin"]


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    @staticmethod
    def get_json(response_data: Any, context: PluginContext) -> dict:
        if isinstance(response_data, Response):
            if response_data.media_type == "application/json":
                return json.loads(response_data.body.decode())
            else:
                raise ValueError(f"Expected 'application/json', but got '{response_data.media_type}'")
        else:
            raise TypeError(f"Expected type must {Response} but got type {type(response_data)}")
