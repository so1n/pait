from typing import List

from flask import Flask, Response, jsonify
from pydantic import ValidationError

from pait import exceptions, field
from pait.app.flask import pait
from pait.param_handle import ParamHandler


class NotTipParamHandler(ParamHandler):
    tip_exception_class = None


def api_exception(exc: Exception) -> Response:
    if isinstance(exc, exceptions.PaitBaseParamException):
        return jsonify({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, ValidationError):
        error_param_list: List = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return jsonify({"code": -1, "msg": f"check error param: {error_param_list}"})
    elif isinstance(exc, exceptions.PaitBaseException):
        return jsonify({"code": -1, "msg": str(exc)})

    return jsonify({"code": -1, "msg": str(exc)})


@pait(param_handler_plugin=NotTipParamHandler)
def demo(demo_value: int = field.Query.i()) -> Response:
    return jsonify({"code": 0, "msg": "", "data": demo_value})


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
