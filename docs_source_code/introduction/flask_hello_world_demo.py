from flask import Flask, Response, jsonify, request


def demo_post() -> Response:
    request_dict = request.json or {}
    uid_str: str = request_dict.get("uid", "")
    username: str = request_dict.get("username", "")

    uid = int(uid_str)  # 暂时不去考虑类型转换的异常
    if not (10 < uid < 1000):
        raise ValueError("invalid uid")
    if not (2 <= len(username) <= 4):
        raise ValueError("invalid name")
    # 获取对应的值进行返回
    return jsonify({"uid": uid, "username": username})


app = Flask("demo")
app.add_url_rule("/api", "demo", demo_post, methods=["POST"])


if __name__ == "__main__":
    app.run(port=8000)
