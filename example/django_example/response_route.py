import os
import sys
import time
from tempfile import NamedTemporaryFile
from typing import Any, Dict

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import FileResponse, HttpResponse, JsonResponse

from example.common import response_model, tag
from example.django_example.utils import global_pait, route_path, run_urlpatterns
from pait.app.django import Pait
from pait.field import Query
from pait.model.status import PaitStatus

check_resp_pait: Pait = global_pait.create_sub_pait(
    group="check_resp", tag=(tag.check_resp_tag,), status=PaitStatus.release
)


@check_resp_pait(response_model_list=[response_model.TextRespModel])
def text_response_route() -> HttpResponse:
    response = HttpResponse(str(time.time()), content_type="text/plain")
    response.headers["X-Example-Type"] = "text"
    return response


@check_resp_pait(response_model_list=[response_model.HtmlRespModel])
def html_response_route() -> HttpResponse:
    response = HttpResponse("<H1>" + str(time.time()) + "</H1>", content_type="text/html")
    response.headers["X-Example-Type"] = "html"
    return response


@check_resp_pait(response_model_list=[response_model.FileRespModel])
def file_response_route() -> FileResponse:
    file_content = "Hello Word!"
    temporary_file = NamedTemporaryFile(delete=True)
    temporary_file.write(file_content.encode())
    temporary_file.seek(0)
    response = FileResponse(temporary_file, as_attachment=False)
    response.headers["X-Example-Type"] = "file"
    return response


@check_resp_pait(
    append_tag=(tag.user_tag,),
    response_model_list=[response_model.UserSuccessRespModel3, response_model.FailRespModel],
)
def check_response_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: str = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display age"),
) -> JsonResponse:
    return_dict: Dict[str, Any] = {
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
    return JsonResponse(return_dict)


urlpatterns = [
    route_path("api/resp/text-resp", text_response_route, ["GET"], name="resp_text"),
    route_path("api/resp/html-resp", html_response_route, ["GET"], name="resp_html"),
    route_path("api/resp/file-resp", file_response_route, ["GET"], name="resp_file"),
    route_path("api/resp/check-resp", check_response_route, ["GET"], name="resp_check"),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.response_route_urlconf")
