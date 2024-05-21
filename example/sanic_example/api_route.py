import hashlib

from sanic import Request, response

from example.common import depend, tag
from example.common.request_model import UserModel
from example.common.response_model import LoginRespModel, SimpleRespModel
from example.sanic_example.utils import create_app
from pait.app.sanic import APIRoute
from pait.field import Depends, Json

user_api_route = APIRoute(path="/user", tag=(tag.user_tag,), group="user")


@user_api_route.get("/info", response_model_list=[SimpleRespModel])
async def get_user_info(user_model: UserModel = Depends.i(depend.GetUserDepend)) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "ok", "data": user_model.dict()})


async def login(
    uid: str = Json.i(description="user id"), password: str = Json.i(description="password")
) -> response.HTTPResponse:
    # only use test
    return response.json(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


user_api_route.add_api_route(login, method=["POST"], path="/login", response_model_list=[LoginRespModel])


health_api_route = APIRoute(path="/", group="health")


@health_api_route.get(path="/health", response_model_list=[SimpleRespModel], tag=(tag.root_api_tag,))
async def health(request: Request) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "ok", "data": {}})


main_api_route = APIRoute(path="/api", tag=(tag.root_api_tag,)).include_sub_route(user_api_route, health_api_route)

if __name__ == "__main__":
    with create_app(__name__) as app:
        main_api_route.inject(app)
