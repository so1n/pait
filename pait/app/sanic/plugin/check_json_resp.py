import json
from typing import Any

from sanic import HTTPResponse

from pait.model.context import ContextModel as PluginContext
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

__all__ = ["CheckJsonRespPlugin"]


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    @staticmethod
    def get_json(response_data: Any, context: PluginContext) -> dict:
        if isinstance(response_data, HTTPResponse):
            if response_data.content_type == "application/json":
                if isinstance(response_data.body, bytes):
                    return json.loads(response_data.body.decode())
                else:
                    return json.loads(str(response_data.body))
            else:
                raise ValueError(f"Expected 'application/json', but got '{response_data.content_type}'")
        else:
            raise TypeError(f"Expected type must {HTTPResponse} but got type {type(response_data)}")
