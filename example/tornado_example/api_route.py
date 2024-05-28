import hashlib

from tornado.web import RequestHandler

from example.common import depend, tag
from example.common.request_model import UserModel
from example.common.response_model import LoginRespModel, SimpleRespModel
from example.tornado_example.utils import create_app
from pait.app.tornado import APIRoute, pait
from pait.field import Depends, Header, Json

user_api_route = APIRoute(path="/user", tag=(tag.user_tag,), group="user")


@user_api_route.get("/info", response_model_list=[SimpleRespModel])
async def get_user_info(request: RequestHandler, user_model: UserModel = Depends.i(depend.GetUserDepend)) -> None:

    return request.write({"code": 0, "msg": "ok", "data": user_model.dict()})


async def login(
    request: RequestHandler, uid: str = Json.i(description="user id"), password: str = Json.i(description="password")
) -> None:
    # only use test
    return request.write(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


user_api_route.add_api_route(login, method=["POST"], path="/login", response_model_list=[LoginRespModel])


health_api_route = APIRoute(path="/", group="health")


@health_api_route.get(path="/health", response_model_list=[SimpleRespModel], tag=(tag.root_api_tag,))
async def health(
    request: RequestHandler,
) -> None:
    request.write({"code": 0, "msg": "ok", "data": {}})


class APIRouteCBVHandler(RequestHandler):
    content_type: str = Header.i(alias="Content-Type")

    @pait()
    async def get(self, user_model: UserModel = Depends.i(depend.GetUserDepend)) -> None:
        self.write({"code": 0, "msg": "ok", "data": user_model.dict(), "content_type": self.content_type})

    async def post(
        self, uid: str = Json.i(description="user id"), password: str = Json.i(description="password")
    ) -> None:
        self.write(
            {
                "code": 0,
                "msg": "",
                "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()},
                "content_type": self.content_type,
            }
        )


user_api_route.add_cbv_route(APIRouteCBVHandler, path="/cbv")
main_api_route = APIRoute(path="/api", tag=(tag.root_api_tag,)).include_sub_route(user_api_route, health_api_route)

if __name__ == "__main__":
    with create_app() as app:
        main_api_route.inject(app)
