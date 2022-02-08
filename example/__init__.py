from typing import List

import uvicorn  # type: ignore
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import exceptions, field
from pait.app.starlette import pait


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, exceptions.TipException):
        # 提取原本的异常
        exc = exc.exc

    if isinstance(exc, exceptions.PaitBaseParamException):
        # 提取参数信息和错误信息，告知用户哪个参数发生错误
        return JSONResponse({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, exceptions.PaitBaseException):
        # 标准的Pait异常，直接返回异常信息
        return JSONResponse({"code": -1, "msg": str(exc)})
    elif isinstance(exc, ValidationError):
        # 解析Pydantic异常，返回校验失败的参数信息
        error_param_list: List[str] = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return JSONResponse({"code": -1, "msg": f"miss param: {error_param_list}"})

    # 路由函数的错误信息
    return JSONResponse({"code": -1, "msg": str(exc)})


@pait()
async def demo(demo_value: int = field.Query.i()) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": demo_value})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)
