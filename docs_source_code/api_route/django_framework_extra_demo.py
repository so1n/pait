import os
import sys
from typing import Any, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import run_urlpatterns
from pait.app.django import APIRoute

api_route = APIRoute(path="/api")


@api_route.get("/health", framework_extra_param={"name": "extra_health"})
def health() -> JsonResponse:
    return JsonResponse({"ok": True})


urlpatterns: List[Any] = []
api_route.inject(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.api_route.django_framework_extra_demo_urlconf")
