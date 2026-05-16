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
    demo_value1: str = field.Query.i(),
    demo_value2: str = field.Query.i(
        not_value_exception_func=lambda param: RuntimeError(f"not found {param.name} data")
    ),
) -> JsonResponse:
    return JsonResponse({"data": {"demo_value1": demo_value1, "demo_value2": demo_value2}})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(
        urlpatterns,
        "docs_source_code.introduction.how_to_use_field.django_with_not_found_exc_demo_urlconf",
    )
