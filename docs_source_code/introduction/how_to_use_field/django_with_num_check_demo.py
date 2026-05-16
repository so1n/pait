import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait.app.django import pait


@pait()
def demo(
    demo_value1: int = field.Query.i(gt=1, lt=10),
    demo_value2: int = field.Query.i(ge=1, le=1),
    demo_value3: int = field.Query.i(multiple_of=3),
) -> JsonResponse:
    return JsonResponse({"data": [demo_value1, demo_value2, demo_value3]})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.how_to_use_field.django_with_num_check_demo_urlconf")
