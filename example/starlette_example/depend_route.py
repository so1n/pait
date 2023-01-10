from typing import Tuple

from starlette.requests import Request
from starlette.responses import JSONResponse

from example.common import depend, tag
from example.common.request_model import UserModel
from example.common.response_model import FailRespModel, SimpleRespModel
from example.starlette_example.utils import api_exception, global_pait
from pait.app.starlette import Pait
from pait.field import Depends, Query
from pait.model.status import PaitStatus

depend_pait: Pait = global_pait.create_sub_pait(
    group="depend",
    status=PaitStatus.release,
    tag=(tag.depend_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)


@depend_pait(append_tag=(tag.user_tag,))
async def depend_route(
    request: Request,
    depend_tuple: Tuple[str, int] = Depends.i(depend.demo_depend),
    user_model: UserModel = Depends.i(depend.AsyncGetUserDepend()),
) -> JSONResponse:
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, "Not found request"
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1], "user_info": user_model.dict()},
        }
    )


@depend_pait(status=PaitStatus.test)
async def depend_contextmanager_route(
    uid: str = Depends.i(depend.context_depend), is_raise: bool = Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


@depend_pait(status=PaitStatus.test, pre_depend_list=[depend.context_depend])
async def pre_depend_contextmanager_route(is_raise: bool = Query.i(default=False)) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": ""})


@depend_pait(status=PaitStatus.test, pre_depend_list=[depend.async_context_depend])
async def pre_depend_async_contextmanager_route(is_raise: bool = Query.i(default=False)) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": ""})


@depend_pait(status=PaitStatus.test)
async def depend_async_contextmanager_route(
    uid: str = Depends.i(depend.async_context_depend), is_raise: bool = Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


if __name__ == "__main__":
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route

    from pait.app.starlette import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Starlette = Starlette(
        routes=[
            Route("/api/depend", depend_route, methods=["POST"]),
            Route("/api/check_depend_contextmanager", depend_contextmanager_route, methods=["GET"]),
            Route("/api/check_depend_async_contextmanager", depend_async_contextmanager_route, methods=["GET"]),
            Route("/api/check_pre_depend_contextmanager", pre_depend_contextmanager_route, methods=["GET"]),
            Route("/api/check_pre_depend_async_contextmanager", pre_depend_async_contextmanager_route, methods=["GET"]),
        ]
    )
    app.add_exception_handler(Exception, api_exception)
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    uvicorn.run(app)
