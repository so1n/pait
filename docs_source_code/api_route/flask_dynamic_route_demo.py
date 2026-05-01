from flask import Flask

from pait.app.flask import APIRoute
from pait.field import Json

api_route = APIRoute(path="/api")


def greet(name: str = Json.i()) -> dict:
    return {"message": f"Hello {name}"}


api_route.add_api_route(greet, method=["POST"], path="/greet", desc="Greeting API")


def create_app() -> Flask:
    app = Flask(__name__)
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
