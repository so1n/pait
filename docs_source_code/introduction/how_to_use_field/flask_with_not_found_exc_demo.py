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
    demo_value1: str = field.Query.i(),
    demo_value2: str = field.Query.i(
        not_value_exception_func=lambda param: RuntimeError(f"not found {param.name} data")
    ),
) -> dict:
    return {"data": {"demo_value1": demo_value1, "demo_value2": demo_value2}}


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
