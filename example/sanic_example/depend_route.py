from typing import Tuple

from sanic import Request, response

from example.common import depend, tag
from example.common.request_model import UserModel
from example.common.response_model import FailRespModel, SimpleRespModel
from example.sanic_example.utils import create_app, global_pait
from pait.app.sanic import Pait
from pait.field import Depends, Query
from pait.model import PaitStatus

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
) -> response.HTTPResponse:
    """Testing depend and using request parameters"""
    assert request is not None, "Not found request"
    return response.json(
        {
            "code": 0,
            "msg": "",
            "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1], "user_info": user_model.dict()},
        }
    )


@depend_pait(status=PaitStatus.test)
async def depend_contextmanager_route(
    uid: int = Depends.i(depend.context_depend), is_raise: bool = Query.i(default=False)
) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": uid})


@depend_pait(status=PaitStatus.test, pre_depend_list=[depend.context_depend])
async def pre_depend_contextmanager_route(is_raise: bool = Query.i(default=False)) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": ""})


@depend_pait(status=PaitStatus.test)
async def depend_async_contextmanager_route(
    uid: int = Depends.i(depend.async_context_depend), is_raise: bool = Query.i(default=False)
) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": uid})


@depend_pait(status=PaitStatus.test, pre_depend_list=[depend.async_context_depend])
async def pre_depend_async_contextmanager_route(is_raise: bool = Query.i(default=False)) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": ""})


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_route(depend_route, "/api/depend", methods={"POST"})
        app.add_route(depend_contextmanager_route, "/api/depend-contextmanager", methods={"GET"})
        app.add_route(pre_depend_contextmanager_route, "/api/pre-depend-contextmanager", methods={"GET"})
        app.add_route(depend_async_contextmanager_route, "/api/depend-async-contextmanager", methods={"GET"})
        app.add_route(pre_depend_async_contextmanager_route, "/api/pre-depend-async-contextmanager", methods={"GET"})
