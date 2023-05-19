from typing import Tuple

from tornado.httputil import HTTPServerRequest

from example.common import depend, tag
from example.common.request_model import UserModel
from example.common.response_model import FailRespModel, SimpleRespModel
from example.tornado_example.utils import MyHandler, create_app, global_pait
from pait.app.tornado import Pait
from pait.field import Depends, Query
from pait.model import PaitStatus

depend_pait: Pait = global_pait.create_sub_pait(
    group="depend",
    status=PaitStatus.release,
    tag=(tag.depend_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)


class DependHandler(MyHandler):
    @depend_pait(append_tag=(tag.user_tag,))
    async def post(
        self,
        request: HTTPServerRequest,
        depend_tuple: Tuple[str, int] = Depends.i(depend.demo_depend),
        user_model: UserModel = Depends.i(depend.AsyncGetUserDepend()),
    ) -> None:
        """Testing depend and using request parameters"""
        assert request is not None, "Not found request"
        self.write(
            {
                "code": 0,
                "msg": "",
                "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1], "user_info": user_model.dict()},
            }
        )


class DependContextmanagerHanler(MyHandler):
    @depend_pait(status=PaitStatus.test)
    async def get(self, uid: int = Depends.i(depend.context_depend), is_raise: bool = Query.i(default=False)) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": uid})


class DependAsyncContextmanagerHanler(MyHandler):
    @depend_pait(status=PaitStatus.test)
    async def get(
        self, uid: int = Depends.i(depend.async_context_depend), is_raise: bool = Query.i(default=False)
    ) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": uid})


class PreDependContextmanagerHanler(MyHandler):
    @depend_pait(status=PaitStatus.test, pre_depend_list=[depend.async_context_depend])
    async def get(self, is_raise: bool = Query.i(default=False)) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": ""})


class PreDependAsyncContextmanagerHanler(MyHandler):
    @depend_pait(status=PaitStatus.test, pre_depend_list=[depend.async_context_depend])
    async def get(self, is_raise: bool = Query.i(default=False)) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": ""})


if __name__ == "__main__":
    with create_app() as app:
        app.add_route(
            [
                (r"/api/depend", DependHandler),
                (r"/api/depend-contextmanager", DependContextmanagerHanler),
                (r"/api/depend-async-contextmanager", DependAsyncContextmanagerHanler),
                (r"/api/pre-depend-contextmanager", PreDependContextmanagerHanler),
                (r"/api/pre-depend-async-contextmanager", PreDependAsyncContextmanagerHanler),
            ]
        )
