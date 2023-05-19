import time
from tempfile import NamedTemporaryFile
from typing import Optional

from flask import Response, make_response, send_from_directory

from example.common import response_model, tag
from example.flask_example.utils import create_app, global_pait
from pait.app.flask import Pait
from pait.field import Query
from pait.model import PaitStatus

check_resp_pait: Pait = global_pait.create_sub_pait(
    group="check_resp", tag=(tag.check_resp_tag,), status=PaitStatus.release
)


@check_resp_pait(response_model_list=[response_model.TextRespModel])
def text_response_route() -> Response:
    """test return text response"""
    response: Response = make_response(str(time.time()), 200)
    response.mimetype = "text/plain"
    response.headers.add_header("X-Example-Type", "text")
    return response


@check_resp_pait(response_model_list=[response_model.HtmlRespModel])
def html_response_route() -> Response:
    """test return html response"""
    response: Response = make_response("<H1>" + str(time.time()) + "</H1>", 200)
    response.mimetype = "text/html"
    response.headers.add_header("X-Example-Type", "html")
    return response


@check_resp_pait(response_model_list=[response_model.FileRespModel])
def file_response_route() -> Response:
    """test return file response"""
    file_content: str = "Hello Word!"
    with NamedTemporaryFile(delete=True) as f:
        f.write(file_content.encode())
        f.seek(0)
        _, f_path, f_filename = f.name.split("/")
        response: Response = send_from_directory("/" + f_path, f_filename)
        response.headers.add_header("X-Example-Type", "file")
        return response


@check_resp_pait(
    append_tag=(tag.user_tag,),
    response_model_list=[response_model.UserSuccessRespModel3, response_model.FailRespModel],
)
def check_response_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display age"),
) -> dict:
    """Test test-helper check response"""
    return_dict: dict = {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
        },
    }
    if display_age == 1:
        return_dict["data"]["age"] = age
    return return_dict


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_url_rule("/api/text-resp", view_func=text_response_route, methods=["GET"])
        app.add_url_rule("/api/html-resp", view_func=html_response_route, methods=["GET"])
        app.add_url_rule("/api/file-resp", view_func=file_response_route, methods=["GET"])
        app.add_url_rule("/api/check-resp", view_func=check_response_route, methods=["GET"])
