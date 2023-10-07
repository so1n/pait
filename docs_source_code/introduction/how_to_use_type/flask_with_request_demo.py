from flask import Flask, Request, Response, jsonify

from pait.app.flask import pait


@pait()
def demo(req: Request) -> Response:
    return jsonify({"url": req.path, "method": req.method})


app = Flask("demo")
app.add_url_rule("/api/demo", "demo", demo, methods=["GET"])


if __name__ == "__main__":
    app.run(port=8000)
