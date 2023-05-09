from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json

from benchmarks.common import RequestDataModel
from pait import field
from pait.app.sanic import pait

token_db_dict: dict = {}


async def get_user_id_by_token(token: str = field.Header.t()) -> str:
    return token_db_dict.get(token, "")


@pait()
async def user_info_by_pait(
    uid: str = field.Depends.i(get_user_id_by_token),
    name: str = field.Query.t(),
    age: int = field.Query.t(),
    sex: str = field.Query.t(),
) -> HTTPResponse:
    return json(
        {
            "uid": uid,
            "name": name,
            "age": age,
            "sex": sex,
        }
    )


async def user_info(request: Request) -> HTTPResponse:
    return json(
        RequestDataModel(
            uid=token_db_dict.get(request.headers.get("token", ""), ""),
            name=request.args.get("name", ""),
            age=int(request.args.get("age", 0)),
            sex=request.args.get("sex", ""),
        ).dict()
    )


def create_app() -> Sanic:
    app = Sanic("benchmarks")
    app.add_route(user_info_by_pait, "/api/user-info-by-pait")
    app.add_route(user_info, "/api/user-info")
    return app
