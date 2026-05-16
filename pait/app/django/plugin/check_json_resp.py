import json
from typing import Any

from django.http import JsonResponse

from pait.model.context import ContextModel as PluginContext
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

__all__ = ["CheckJsonRespPlugin"]


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    @staticmethod
    def get_json(response_data: Any, context: PluginContext) -> dict:
        if isinstance(response_data, JsonResponse):
            return json.loads(response_data.content.decode(response_data.charset))
        else:
            raise TypeError(f"Expected type must {JsonResponse} but got type {type(response_data)}")
