import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import HttpRequest, JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait


@pait()
def demo(req: HttpRequest) -> JsonResponse:
    return JsonResponse({"url": req.path, "method": req.method})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.how_to_use_type.django_with_request_demo_urlconf")
