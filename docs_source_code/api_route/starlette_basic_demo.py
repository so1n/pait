import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from pait.app.starlette import APIRoute
from pait.field import Json, Path
from pait.model.tag import Tag

# Create an API route group.
api_route = APIRoute(path="/api", tag=(Tag("api-route-demo"),), group="demo")


@api_route.get("/users")
async def get_users() -> JSONResponse:
    """Get user list"""
    return JSONResponse({"code": 0, "msg": "ok", "data": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]})


@api_route.post("/users")
async def create_user(
    name: str = Json.i(description="User name"), age: int = Json.i(description="User age")
) -> JSONResponse:
    """Create a new user"""
    return JSONResponse({"code": 0, "msg": "ok", "data": {"id": 3, "name": name, "age": age}})


@api_route.get("/users/{user_id}")
async def get_user(user_id: int = Path.t()) -> JSONResponse:
    """Get one user"""
    return JSONResponse({"code": 0, "msg": "ok", "data": {"id": user_id, "name": "User " + str(user_id)}})


def create_app() -> Starlette:
    app = Starlette()
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
