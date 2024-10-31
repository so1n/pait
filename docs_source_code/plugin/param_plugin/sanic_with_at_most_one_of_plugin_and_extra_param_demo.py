from typing import Optional

from sanic import Request, Sanic
from sanic.response import HTTPResponse, json

from pait import field
from pait.app.sanic import pait
from pait.exceptions import TipException
from pait.plugin.at_most_one_of import AtMostOneOfExtraParam, AtMostOneOfPlugin


async def api_exception(request: Request, exc: Exception) -> HTTPResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return json({"data": str(exc)})


@pait(post_plugin_list=[AtMostOneOfPlugin.build()])
async def demo(
    uid: str = field.Query.i(),
    email: Optional[str] = field.Query.i(default=None, extra_param_list=[AtMostOneOfExtraParam(group="my-group")]),
    user_name: Optional[str] = field.Query.i(default=None, extra_param_list=[AtMostOneOfExtraParam(group="my-group")]),
) -> HTTPResponse:
    return json({"uid": uid, "user_name": user_name, "email": email})


app = Sanic("demo", configure_logging=False)
app.add_route(demo, "/api/demo", methods=["GET"])
app.exception(Exception)(api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
