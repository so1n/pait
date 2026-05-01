from sanic import Sanic
from sanic.response import json

from pait.app.sanic import APIRoute
from pait.field import Json

api_route = APIRoute(path="/api")


async def greet(name: str = Json.i()):
    return json({"message": f"Hello {name}"})


api_route.add_api_route(greet, method=["POST"], path="/greet", desc="Greeting API")


def create_app() -> Sanic:
    app = Sanic("api_route_dynamic_demo")
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
