from typing import List

from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import exceptions, field
from pait.app.starlette import pait


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, exceptions.TipException):
        exc = exc.exc

    if isinstance(exc, exceptions.PaitBaseParamException):
        return JSONResponse({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, ValidationError):
        error_param_list: List = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return JSONResponse({"code": -1, "msg": f"check error param: {error_param_list}"})
    elif isinstance(exc, exceptions.PaitBaseException):
        return JSONResponse({"code": -1, "msg": str(exc)})

    return JSONResponse({"code": -1, "msg": str(exc)})


@pait()
async def demo(demo_value: int = field.Query.i()) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": demo_value})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
