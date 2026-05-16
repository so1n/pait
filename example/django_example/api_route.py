import hashlib
import os
import sys
from typing import Any, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse
from django.views import View

from example.common import depend, tag
from example.common.request_model import UserModel
from example.common.response_model import LoginRespModel, SimpleRespModel
from example.django_example.utils import run_urlpatterns
from pait.app.django import APIRoute, pait
from pait.field import Depends, Header, Json

user_api_route = APIRoute(path="/user", tag=(tag.user_tag,), group="user")


@user_api_route.get("/info", response_model_list=[SimpleRespModel])
def get_user_info(user_model: UserModel = Depends.i(depend.GetUserDepend)) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "ok", "data": user_model.dict()})


def login(uid: str = Json.i(description="user id"), password: str = Json.i(description="password")) -> JsonResponse:
    return JsonResponse(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


user_api_route.add_api_route(login, method=["POST"], path="/login", response_model_list=[LoginRespModel])

health_api_route = APIRoute(path="/", group="health")


@health_api_route.get(path="/health", response_model_list=[SimpleRespModel], tag=(tag.root_api_tag,))
def health() -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "ok", "data": {}})


class APIRouteCBV(View):
    content_type: str = Header.i(alias="Content-Type")

    @pait()
    def get(self, user_model: UserModel = Depends.i(depend.GetUserDepend)) -> JsonResponse:
        return JsonResponse({"code": 0, "msg": "ok", "data": user_model.dict(), "content_type": self.content_type})

    def post(self, uid: str = Json.i(), password: str = Json.i()) -> JsonResponse:
        return JsonResponse(
            {
                "code": 0,
                "msg": "",
                "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()},
                "content_type": self.content_type,
            }
        )


user_api_route.add_cbv_route(APIRouteCBV, path="/cbv")
main_api_route = APIRoute(path="/api", tag=(tag.root_api_tag,)).include_sub_route(user_api_route, health_api_route)

urlpatterns: List[Any] = []
main_api_route.inject(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.api_route_urlconf")
