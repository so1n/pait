import datetime

from flask import Flask, Response, jsonify

from pait import field
from pait.app.flask import pait


@pait()
def demo(timestamp: datetime.datetime = field.Query.i()) -> Response:
    return jsonify({"time": timestamp.isoformat()})


app = Flask("demo")
app.add_url_rule("/api/demo", "demo", demo, methods=["GET"])


if __name__ == "__main__":
    app.run(port=8000)
