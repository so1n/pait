import json

from starlette.responses import JSONResponse

from pait.plugin.check_json_resp import AsyncCheckJsonRespPlugin as _CheckJsonRespPlugin


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    def get_dict_by_resp(self, resp: JSONResponse) -> dict:
        if isinstance(resp, JSONResponse):
            raise TypeError(f"{self.__class__.__name__} not support resp. Resp type must {JSONResponse}")
        return json.loads(resp.body)
