from flask import Flask

from pait.app.flask import APIRoute

api_route = APIRoute(path="/api")


@api_route.get("/health", framework_extra_param={"endpoint": "extra_health"})
def health() -> dict:
    return {"ok": True}


def create_app() -> Flask:
    app = Flask(__name__)
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
