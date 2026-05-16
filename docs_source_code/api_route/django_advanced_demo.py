import os
import sys
from typing import Any, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse
from django.views import View

from example.django_example.utils import run_urlpatterns
from pait.app.django import APIRoute, pait
from pait.field import Header, Json
from pait.model.tag import Tag

user_api_route = APIRoute(path="/user", tag=(Tag("api-route-user"),), group="user")


@user_api_route.get("/profile")
def get_profile(user_id: int = Header.i(alias="X-User-ID", description="User ID")) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "ok", "data": {"user_id": user_id, "name": "User Profile"}})


def login(
    username: str = Json.i(description="Username"), password: str = Json.i(description="Password")
) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "ok", "data": {"token": f"token_for_{username}"}})


user_api_route.add_api_route(login, method=["POST"], path="/login")


class OrderAPIView(View):
    def get(self, order_id: int = Header.i(alias="X-Order-ID", description="Order ID")) -> JsonResponse:
        return JsonResponse({"code": 0, "msg": "ok", "data": {"order_id": order_id, "status": "completed"}})

    @pait()
    def post(
        self, total: float = Json.i(description="Order total"), items: list = Json.i(description="Order items")
    ) -> JsonResponse:
        return JsonResponse({"code": 0, "msg": "ok", "data": {"order_id": 12345, "total": total, "items": items}})


order_api_route = APIRoute(path="/order", tag=(Tag("api-route-order"),), group="order")
order_api_route.add_cbv_route(OrderAPIView, path="/manage")

main_api_route = APIRoute(path="/api/v1", tag=(Tag("api-route-v1"),)).include_sub_route(user_api_route, order_api_route)

urlpatterns: List[Any] = []
main_api_route.inject(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.api_route.django_advanced_demo_urlconf")
