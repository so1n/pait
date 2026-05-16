import os
import sys
from typing import Any, Dict, Type

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse
from pydantic import BaseModel, Field

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.app.django.plugin import CheckJsonRespPlugin
from pait.field import Query
from pait.model.response import JsonResponseModel


class UserSuccessRespModel3(JsonResponseModel):
    class ResponseModel(BaseModel):  # type: ignore
        class DataModel(BaseModel):
            uid: int = Field(description="user id", gt=10, lt=1000)
            user_name: str = Field(description="user name", min_length=2, max_length=4)
            age: int = Field(description="age", gt=1, lt=100)
            email: str = Field(description="user email")

        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
def demo(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: str = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> JsonResponse:
    return_dict: Dict[str, Any] = {"code": 0, "msg": "", "data": {"uid": uid, "user_name": user_name, "email": email}}
    if display_age == 1:
        return_dict["data"]["age"] = age
    return JsonResponse(return_dict)


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.plugin.json_plugin.django_with_check_json_plugin_demo_urlconf")
