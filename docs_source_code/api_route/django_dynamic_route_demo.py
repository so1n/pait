import os
import sys
from typing import Any, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import run_urlpatterns
from pait.app.django import APIRoute
from pait.field import Json

api_route = APIRoute(path="/api")


def greet(name: str = Json.i()) -> JsonResponse:
    return JsonResponse({"message": f"Hello {name}"})


api_route.add_api_route(greet, method=["POST"], path="/greet", desc="Greeting API")

urlpatterns: List[Any] = []
api_route.inject(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.api_route.django_dynamic_route_demo_urlconf")
