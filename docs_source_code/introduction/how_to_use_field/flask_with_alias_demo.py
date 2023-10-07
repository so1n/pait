from flask import Flask

from pait import field
from pait.app.flask import pait


@pait()
def demo(content_type: str = field.Header.t(alias="Content-Type")) -> str:
    return content_type


app = Flask("demo")

app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])


if __name__ == "__main__":
    app.run(port=8000)
