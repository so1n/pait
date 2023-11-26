from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def demo_post(request: Request) -> JSONResponse:
    request_dict = await request.json()
    uid_str: str = request_dict.get("uid", "")
    username: str = request_dict.get("username", "")

    uid = int(uid_str)  # Don't think about type conversion exceptions for now
    if not (10 < uid < 1000):
        raise ValueError("invalid uid")
    if not (2 <= len(username) <= 4):
        raise ValueError("invalid name")
    # get the corresponding value and return it
    return JSONResponse({"uid": uid, "username": username})


app = Starlette(routes=[Route("/api", demo_post, methods=["POST"])])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
