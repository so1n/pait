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
    demo_value: dict = field.Body.i(raw_return=True),
    a: str = field.Body.i(),
) -> dict:
    return {"data": demo_value, "a": a}


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["POST"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
