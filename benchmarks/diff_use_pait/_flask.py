from flask import Flask, Response, jsonify, request

from benchmarks.common import RequestDataModel
from pait import field
from pait.app.flask import pait

token_db_dict: dict = {}


def get_user_id_by_token(token: str = field.Header.t()) -> str:
    return token_db_dict.get(token, "")


@pait()
def user_info_by_pait(
    uid: str = field.Depends.t(get_user_id_by_token),
    name: str = field.Query.t(),
    age: int = field.Query.t(),
    sex: str = field.Query.t(),
) -> Response:
    return jsonify(
        {
            "uid": uid,
            "name": name,
            "age": age,
            "sex": sex,
        }
    )


def user_info() -> Response:
    return jsonify(
        RequestDataModel(
            uid=token_db_dict.get(request.headers.get("token", ""), ""),
            name=request.args.get("name", ""),
            age=int(request.args.get("age", 0)),
            sex=request.args.get("sex", ""),
        ).dict()
    )


def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule("/api/user-info-by-pait", view_func=user_info_by_pait, methods=["GET"])
    app.add_url_rule("/api/user-info", view_func=user_info, methods=["GET"])
    return app
