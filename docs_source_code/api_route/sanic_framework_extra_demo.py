from sanic import Sanic
from sanic.response import json

from pait.app.sanic import APIRoute

api_route = APIRoute(path="/api")


@api_route.get("/health", framework_extra_param={"name": "extra_health"})
async def health():
    return json({"ok": True})


def create_app() -> Sanic:
    app = Sanic("api_route_framework_extra_demo")
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
