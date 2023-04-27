from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from benchmarks.common import RequestDataModel
from pait import field
from pait.app.starlette import pait

token_db_dict: dict = {}


async def get_user_id_by_token(token: str = field.Header.t()) -> str:
    return token_db_dict.get(token, "")


@pait()
async def user_info_by_pait(
    uid: str = field.Depends.i(get_user_id_by_token),
    name: str = field.Query.t(),
    age: int = field.Query.t(),
    sex: str = field.Query.t(),
) -> JSONResponse:
    return JSONResponse(
        {
            "uid": uid,
            "name": name,
            "age": age,
            "sex": sex,
        }
    )


async def user_info(request: Request) -> JSONResponse:
    return JSONResponse(
        RequestDataModel(
            uid=token_db_dict.get(request.headers.get("token", ""), ""),
            name=request.query_params.get("name", ""),
            age=int(request.query_params.get("age", 0)),
            sex=request.query_params.get("sex", ""),
        ).dict()
    )


def create_app() -> Starlette:
    app = Starlette(__name__)
    app.add_route("/api/user-info-by-pait", user_info_by_pait, methods=["GET"])
    app.add_route("/api/user-info", user_info, methods=["GET"])
    return app
