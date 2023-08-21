from typing import Any

from flask import Response

from pait.model.context import ContextModel as PluginContext
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

__all__ = ["CheckJsonRespPlugin"]


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    @staticmethod
    def get_json(response_data: Any, context: PluginContext) -> dict:
        if isinstance(response_data, Response):
            return response_data.get_json()
        else:
            raise TypeError(f"Expected type must {Response} but got type {type(response_data)}")
