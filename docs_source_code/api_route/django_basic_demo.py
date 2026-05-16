import os
import sys
from typing import Any, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import run_urlpatterns
from pait.app.django import APIRoute
from pait.field import Json, Path

api_route = APIRoute(path="/api/users", group="api-route-users")


@api_route.get("", name="list_users")
def get_users() -> JsonResponse:
    return JsonResponse({"data": [{"id": 1, "name": "so1n"}, {"id": 2, "name": "appl"}]})


@api_route.post("/create", name="create_user")
def create_user(name: str = Json.i(), age: int = Json.i()) -> JsonResponse:
    return JsonResponse({"data": {"id": 3, "name": name, "age": age}})


@api_route.get("/{user_id}", name="get_user")
def get_user(user_id: int = Path.i()) -> JsonResponse:
    return JsonResponse({"data": {"id": user_id, "name": "so1n"}})


urlpatterns: List[Any] = []
api_route.inject(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.api_route.django_basic_demo_urlconf")
