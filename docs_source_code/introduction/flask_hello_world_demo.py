from flask import Flask, Response, jsonify, request


def demo_post() -> Response:
    request_dict = request.json or {}
    uid_str: str = request_dict.get("uid", "")
    username: str = request_dict.get("username", "")

    uid = int(uid_str)  # Don't think about type conversion exceptions for now
    if not (10 < uid < 1000):
        raise ValueError("invalid uid")
    if not (2 <= len(username) <= 4):
        raise ValueError("invalid name")
    # get the corresponding value and return it
    return jsonify({"uid": uid, "username": username})


app = Flask("demo")
app.add_url_rule("/api", "demo", demo_post, methods=["POST"])


if __name__ == "__main__":
    app.run(port=8000)
