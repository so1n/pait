import os
import sys
from typing import Any, Dict, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import HttpRequest, JsonResponse

from example.common import tag
from example.common.request_model import SexEnum, TestPaitModel, UserModel, UserOtherModel
from example.common.response_model import FailRespModel, SimpleRespModel, UserSuccessRespModel
from example.django_example.utils import global_pait, route_path, run_urlpatterns
from pait.app.django import Pait
from pait.field import Cookie, File, Form, Header, Json, MultiForm, MultiQuery, Path, Query
from pait.model.status import PaitStatus

field_pait: Pait = global_pait.create_sub_pait(group="field", status=PaitStatus.release, tag=(tag.field_tag,))


@field_pait(append_tag=(tag.user_tag, tag.post_tag), response_model_list=[UserSuccessRespModel, FailRespModel])
def post_route(
    request: HttpRequest,
    model: UserModel = Json.i(raw_return=True),
    other_model: UserOtherModel = Json.i(raw_return=True),
    sex: SexEnum = Json.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
) -> JsonResponse:
    assert request is not None, "Not found request"
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return JsonResponse({"code": 0, "msg": "", "data": return_dict})


@field_pait(response_model_list=[FailRespModel])
def query_route(uid: int = Query.i(description="user id"), user_name: str = Query.i()) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": {"uid": uid, "user_name": user_name}})


@field_pait(tag=(tag.same_alias_tag,), response_model_list=[SimpleRespModel, FailRespModel])
def same_alias_route(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}})


@field_pait(response_model_list=[SimpleRespModel, FailRespModel])
def field_default_factory_route(
    demo_value: int = Json.i(description="Json body value not empty"),
    data_list: List[str] = Json.i(default_factory=list, description="test default factory"),
    data_dict: Dict[str, Any] = Json.i(default_factory=dict, description="test default factory"),
) -> JsonResponse:
    return JsonResponse(
        {"code": 0, "msg": "", "data": {"demo_value": demo_value, "data_list": data_list, "data_dict": data_dict}}
    )


@field_pait(response_model_list=[SimpleRespModel, FailRespModel])
def pait_base_field_route(
    upload_file: Any = File.i(description="upload file"),
    a: str = Form.i(description="form data"),
    b: str = Form.i(description="form data"),
    c: List[str] = MultiForm.i(description="form data"),
    cookie: dict = Cookie.i(raw_return=True, description="cookie"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: str = Query.i(default="example@xxx.com", description="user email"),
    sex: SexEnum = Query.i(description="sex"),
) -> JsonResponse:
    return JsonResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "filename": upload_file.name,
                "content": upload_file.read().decode(),
                "form_a": a,
                "form_b": b,
                "form_c": c,
                "cookie": cookie,
                "multi_user_name": multi_user_name,
                "age": age,
                "uid": uid,
                "user_name": user_name,
                "email": email,
                "sex": sex.value,
            },
        }
    )


@field_pait(status=PaitStatus.test, response_model_list=[SimpleRespModel, FailRespModel])
def pait_model_route(test_pait_model: TestPaitModel) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": test_pait_model.dict()})


class Demo(object):
    pass


@field_pait()
def any_type_route(demo: "Demo" = Demo()) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": id(demo)})


urlpatterns = [
    route_path("api/field/post", post_route, ["POST"], name="field_post"),
    route_path("api/field/query", query_route, ["GET"], name="field_query"),
    route_path("api/field/pait-base-field/<int:age>", pait_base_field_route, ["POST"], name="field_pait_base_field"),
    route_path("api/field/field-default-factory", field_default_factory_route, ["POST"], name="field_default_factory"),
    route_path("api/field/same-alias", same_alias_route, ["GET"], name="field_same_alias"),
    route_path("api/field/pait-model", pait_model_route, ["POST"], name="field_pait_model"),
    route_path("api/field/any-type", any_type_route, ["POST"], name="field_any_type"),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.field_route_urlconf")
