import httpx
from flask import Flask, Response, current_app, jsonify

from pait.app import get_app_attribute, set_app_attribute


def demo_route() -> Response:
    client: httpx.Client = get_app_attribute(current_app, "client")
    return jsonify({"status_code": client.get("http://so1n.me").status_code})


app: Flask = Flask("demo")
app.add_url_rule("/api/demo", "demo", demo_route, methods=["GET"])
set_app_attribute(app, "client", httpx.Client())


if __name__ == "__main__":
    app.run(port=8000)
