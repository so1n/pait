import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait.app.django import pait


@pait()
def demo(demo_value: dict = field.Json.i(raw_return=True), a: str = field.Json.i()) -> JsonResponse:
    return JsonResponse({"data": demo_value, "a": a})


urlpatterns = [route_path("api/demo", demo, ["POST"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.how_to_use_field.django_with_raw_return_demo_urlconf")
