from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json


async def demo_post(request: Request) -> HTTPResponse:
    request_dict = await request.json()
    uid_str: str = request_dict.get("uid", "")
    username: str = request_dict.get("username", "")

    uid = int(uid_str)  # Don't think about type conversion exceptions for now
    if not (10 < uid < 1000):
        raise ValueError("invalid uid")
    if not (2 <= len(username) <= 4):
        raise ValueError("invalid name")
    # get the corresponding value and return it
    return json({"uid": uid, "username": username})


app = Sanic(name="demo", configure_logging=False)
app.add_route(demo_post, "/api", methods=["POST"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
