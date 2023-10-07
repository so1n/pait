from typing import Optional

from flask import Flask, Response, jsonify

from pait import field
from pait.app.flask import pait
from pait.exceptions import TipException
from pait.plugin.required import RequiredPlugin


def api_exception(exc: Exception) -> Response:
    if isinstance(exc, TipException):
        exc = exc.exc
    return jsonify({"data": str(exc)})


@pait(post_plugin_list=[RequiredPlugin.build(required_dict={"email": ["user_name"]})])
def demo(
    uid: str = field.Query.i(),
    user_name: Optional[str] = field.Query.i(default=None),
    email: Optional[str] = field.Query.i(default=None),
) -> Response:
    return jsonify({"uid": uid, "user_name": user_name, "email": email})


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
