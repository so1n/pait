from flask import Response, current_app

from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin


class CheckJsonRespPlugin(_CheckJsonRespPlugin):
    def get_dict_by_resp(self, resp: Response) -> dict:
        assert isinstance(resp, Response), f"resp must {Response}"
        if resp.mimetype != current_app.config["JSONIFY_MIMETYPE"]:
            raise TypeError(f"{self.__class__.__name__} not support resp. mimetype:{resp.mimetype}")
        return resp.get_json()
