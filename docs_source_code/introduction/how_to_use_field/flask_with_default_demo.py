from flask import Flask

from pait import field
from pait.app.flask import pait
from pait.exceptions import TipException


def api_exception(exc: Exception) -> str:
    if isinstance(exc, TipException):
        exc = exc.exc
    return str(exc)


@pait()
def demo(demo_value: str = field.Query.t(default="123")) -> str:
    return demo_value


@pait()
def demo1(demo_value: str = field.Query.t()) -> str:
    return demo_value


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.add_url_rule("/api/demo1", view_func=demo1, methods=["GET"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
