from sanic.app import Sanic
from sanic.response import HTTPResponse, json

from pait.app.sanic import pait
from pait.field import Json


@pait()
async def demo_post(
    uid: int = Json.t(description="user id", gt=10, lt=1000),
    username: str = Json.t(description="user name", min_length=2, max_length=4),
) -> HTTPResponse:
    return json({"uid": uid, "user_name": username})


app = Sanic(name="demo", configure_logging=False)
app.add_route(demo_post, "/api", methods=["POST"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
