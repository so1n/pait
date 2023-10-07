from typing import Optional

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait
from pait.exceptions import TipException
from pait.plugin.at_most_one_of import AtMostOneOfExtraParam, AtMostOneOfPlugin


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


@pait(post_plugin_list=[AtMostOneOfPlugin.build()])
async def demo(
    uid: str = field.Query.i(),
    email: Optional[str] = field.Query.i(default=None, extra_param_list=[AtMostOneOfExtraParam(group="my-group")]),
    user_name: Optional[str] = field.Query.i(default=None, extra_param_list=[AtMostOneOfExtraParam(group="my-group")]),
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name, "email": email})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
