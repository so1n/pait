import tornado.ioloop
import tornado.web

from pait.app.tornado import APIRoute
from pait.field import Json, Path
from pait.model.tag import Tag

# Create an API route group.
api_route = APIRoute(path="/api", tag=(Tag("api-route-demo"),), group="demo")


@api_route.get("/users")
def get_users(request: tornado.web.RequestHandler) -> None:
    """Get user list"""
    request.write({"code": 0, "msg": "ok", "data": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]})


@api_route.post("/users")
def create_user(
    request: tornado.web.RequestHandler,
    name: str = Json.i(description="User name"),
    age: int = Json.i(description="User age"),
) -> None:
    """Create a new user"""
    request.write({"code": 0, "msg": "ok", "data": {"id": 3, "name": name, "age": age}})


@api_route.get("/users/{user_id}")
def get_user(request: tornado.web.RequestHandler, user_id: int = Path.t()) -> None:
    """Get one user"""
    request.write({"code": 0, "msg": "ok", "data": {"id": user_id, "name": "User " + str(user_id)}})


def make_app():
    app = tornado.web.Application()
    api_route.inject(app)
    return app


app = make_app()


if __name__ == "__main__":
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
