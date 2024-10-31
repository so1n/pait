from typing import Optional

from sanic import Request, Sanic
from sanic.response import HTTPResponse, json

from pait import field
from pait.app.sanic import pait
from pait.exceptions import TipException
from pait.plugin.required import RequiredPlugin


async def api_exception(request: Request, exc: Exception) -> HTTPResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return json({"data": str(exc)})


@pait(post_plugin_list=[RequiredPlugin.build(required_dict={"email": ["user_name"]})])
async def demo(
    uid: str = field.Query.i(),
    user_name: Optional[str] = field.Query.i(default=None),
    email: Optional[str] = field.Query.i(default=None),
) -> HTTPResponse:
    return json({"uid": uid, "user_name": user_name, "email": email})


app = Sanic("demo", configure_logging=False)
app.add_route(demo, "/api/demo", methods=["GET"])
app.exception(Exception)(api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
