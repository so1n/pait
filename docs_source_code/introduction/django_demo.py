import os
import sys
from typing import Type

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse
from pydantic import BaseModel, Field

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.field import Json
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel])
def demo_post(
    uid: int = Json.t(description="user id", gt=10, lt=1000),
    username: str = Json.t(description="user name", min_length=2, max_length=4),
) -> JsonResponse:
    return JsonResponse({"uid": uid, "user_name": username})


urlpatterns = [route_path("api", demo_post, ["POST"], name="demo")]
AddDocRoute(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.django_demo_urlconf")
