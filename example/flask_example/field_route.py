from typing import Any, Dict, List

from example.common import tag
from example.common.request_model import SexEnum, TestPaitModel, UserModel, UserOtherModel
from example.common.response_model import FailRespModel, SimpleRespModel, UserSuccessRespModel
from example.flask_example.utils import create_app, global_pait
from pait.app.flask import Pait
from pait.field import Cookie, File, Form, Header, Json, MultiForm, MultiQuery, Path, Query
from pait.model.status import PaitStatus

field_pait: Pait = global_pait.create_sub_pait(
    group="field",
    status=PaitStatus.release,
    tag=(tag.field_tag,),
)


@field_pait(
    append_tag=(tag.user_tag, tag.post_tag),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
def post_route(
    model: UserModel = Json.i(raw_return=True),
    other_model: UserOtherModel = Json.i(raw_return=True),
    sex: SexEnum = Json.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
) -> dict:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return {"code": 0, "msg": "", "data": return_dict}


@field_pait(
    tag=(tag.same_alias_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def same_alias_route(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> dict:
    """Test different request types, but they have the same alias and different parameter names"""
    return {"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}}


@field_pait(
    response_model_list=[SimpleRespModel, FailRespModel],
)
def field_default_factory_route(
    demo_value: int = Json.i(description="Json body value not empty"),
    data_list: List[str] = Json.i(default_factory=list, description="test default factory"),
    data_dict: Dict[str, Any] = Json.i(default_factory=dict, description="test default factory"),
) -> dict:
    return {"code": 0, "msg": "", "data": {"demo_value": demo_value, "data_list": data_list, "data_dict": data_dict}}


@field_pait(
    response_model_list=[SimpleRespModel, FailRespModel],
)
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
) -> dict:
    """Test the use of all BaseRequestResourceField-based"""
@field_pait(status=PaitStatus.test, response_model_list=[SimpleRespModel, FailRespModel])
def pait_model_route(test_pait_model: TestPaitModel) -> dict:
    """Test pait model"""
    return {"code": 0, "msg": "", "data": test_pait_model.dict()}


class Demo(object):
    pass


@field_pait()
def any_type_route(demo: "Demo" = Demo()) -> dict:
    return {"code": 0, "msg": "", "data": id(demo)}


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_url_rule("/api/post", view_func=post_route, methods=["POST"])
        app.add_url_rule("/api/pait-base-field/<age>", view_func=pait_base_field_route, methods=["POST"])
        app.add_url_rule("/api/field-default-factory", view_func=field_default_factory_route, methods=["POST"])
        app.add_url_rule("/api/same-alias", view_func=same_alias_route, methods=["GET"])
        app.add_url_rule("/api/pait-model", view_func=pait_model_route, methods=["POST"])
        app.add_url_rule("/api/any-type", view_func=any_type_route, methods=["POST"])
