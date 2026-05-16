import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import HttpResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait.app.django import pait


@pait()
def demo(demo_value: str = field.Query.t(default="123")) -> HttpResponse:
    return HttpResponse(demo_value)


@pait()
def demo1(demo_value: str = field.Query.t()) -> HttpResponse:
    return HttpResponse(demo_value)


urlpatterns = [
    route_path("api/demo", demo, ["GET"], name="demo"),
    route_path("api/demo1", demo1, ["GET"], name="demo1"),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.how_to_use_field.django_with_default_demo_urlconf")
