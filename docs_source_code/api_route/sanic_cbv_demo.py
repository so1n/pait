from sanic import Sanic
from sanic.response import json
from sanic.views import HTTPMethodView

from pait.app.sanic import APIRoute, pait
from pait.field import Header, Json

api_route = APIRoute(path="/api")


class UserAPIView(HTTPMethodView):
    async def get(self, user_id: int = Header.i(alias="X-User-ID")):
        return json({"user_id": user_id})

    @pait()
    async def post(self, name: str = Json.i()):
        return json({"created": {"name": name}})


api_route.add_cbv_route(UserAPIView, path="/users")


def create_app() -> Sanic:
    app = Sanic("api_route_cbv_demo")
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
