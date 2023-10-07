from typing import Optional

from flask import Flask, Response, jsonify

from pait import field
from pait.app.flask import pait
from pait.exceptions import TipException
from pait.plugin.at_most_one_of import AtMostOneOfExtraParam, AtMostOneOfPlugin


def api_exception(exc: Exception) -> Response:
    if isinstance(exc, TipException):
        exc = exc.exc
    return jsonify({"data": str(exc)})


@pait(post_plugin_list=[AtMostOneOfPlugin.build()])
def demo(
    uid: str = field.Query.i(),
    email: Optional[str] = field.Query.i(default=None, extra_param_list=[AtMostOneOfExtraParam(group="my-group")]),
    user_name: Optional[str] = field.Query.i(default=None, extra_param_list=[AtMostOneOfExtraParam(group="my-group")]),
) -> Response:
    return jsonify({"uid": uid, "user_name": user_name, "email": email})


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
