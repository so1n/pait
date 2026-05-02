from sanic import Request, Sanic
from sanic.response import json

from pait.app.sanic import APIRoute
from pait.field import Json, Path
from pait.model.tag import Tag

# Create an API route group.
api_route = APIRoute(path="/api", tag=(Tag("api-route-demo"),), group="demo")


@api_route.get("/users")
async def get_users(request: Request):
    """Get user list"""
    return json({"code": 0, "msg": "ok", "data": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]})


@api_route.post("/users")
async def create_user(
    request: Request, name: str = Json.i(description="User name"), age: int = Json.i(description="User age")
):
    """Create a new user"""
    return json({"code": 0, "msg": "ok", "data": {"id": 3, "name": name, "age": age}})


@api_route.get("/users/{user_id}")
async def get_user(request: Request, user_id: int = Path.t()):
    """Get one user"""
    return json({"code": 0, "msg": "ok", "data": {"id": user_id, "name": "User " + str(user_id)}})


def create_app() -> Sanic:
    app = Sanic("api_route_basic_demo")
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
