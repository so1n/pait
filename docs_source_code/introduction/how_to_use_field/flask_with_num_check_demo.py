from flask import Flask, Response, jsonify
from pydantic import ValidationError

from pait import field
from pait.app.flask import pait
from pait.exceptions import TipException


def api_exception(exc: Exception) -> Response:
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return jsonify({"data": exc.errors()})
    return jsonify({"data": str(exc)})


@pait()
def demo(
    demo_value1: int = field.Query.i(gt=1, lt=10),
    demo_value2: int = field.Query.i(ge=1, le=1),
    demo_value3: int = field.Query.i(multiple_of=3),
) -> dict:
    return {"data": [demo_value1, demo_value2, demo_value3]}


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
