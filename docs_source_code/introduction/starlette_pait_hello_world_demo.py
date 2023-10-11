from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body


@pait()
async def demo_post(
    uid: int = Body.t(description="user id", gt=10, lt=1000),
    username: str = Body.t(description="user name", min_length=2, max_length=4),
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": username})


app = Starlette(routes=[Route("/api", demo_post, methods=["POST"])])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
