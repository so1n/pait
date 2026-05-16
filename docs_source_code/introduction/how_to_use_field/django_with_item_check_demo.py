import os
import sys
from typing import List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait.app.django import pait


@pait()
def demo(demo_value: List[int] = field.MultiQuery.i(min_items=1, max_items=2)) -> JsonResponse:
    return JsonResponse({"data": demo_value})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.how_to_use_field.django_with_item_check_demo_urlconf")
