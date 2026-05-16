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

api_route = APIRoute(path="/api")


class UserAPIView(View):
    def get(self, user_id: int = Header.i(alias="X-User-ID")) -> JsonResponse:
        return JsonResponse({"user_id": user_id})

    @pait()
    def post(self, name: str = Json.i()) -> JsonResponse:
        return JsonResponse({"created": {"name": name}})


api_route.add_cbv_route(UserAPIView, path="/users")

urlpatterns: List[Any] = []
api_route.inject(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.api_route.django_cbv_demo_urlconf")
