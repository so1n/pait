from flask import Flask, Response, jsonify

from pait.app.flask import pait
from pait.field import Body


@pait()
def demo_post(
    uid: int = Body.t(description="user id", gt=10, lt=1000),
    username: str = Body.t(description="user name", min_length=2, max_length=4),
) -> Response:
    return jsonify({"uid": uid, "user_name": username})


app = Flask("demo")
app.add_url_rule("/api", "demo", demo_post, methods=["POST"])


if __name__ == "__main__":
    app.run(port=8000)
