import json

from sanic.response import HTTPResponse

from pait.plugin.check_json_resp import AsyncCheckJsonRespPlugin as _CheckJsonRespPlugin


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    def get_dict_by_resp(self, resp: HTTPResponse) -> dict:
        if resp.content_type != "application/json":
            raise TypeError(f"{self.__class__.__name__} not support. Content type must application/json")
        if not getattr(resp.body, "decode", None):
            raise ValueError(f"Can not found body by resp:{resp}")
        return json.loads(resp.body.decode())  # type: ignore
