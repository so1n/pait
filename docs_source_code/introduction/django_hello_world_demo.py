import json
import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import HttpRequest, JsonResponse

from example.django_example.utils import route_path, run_urlpatterns


def demo_post(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body.decode(request.encoding or "utf-8"))
    uid: int = int(body["uid"])
    username: str = body["username"]

    if not 10 < uid < 1000:
        raise ValueError("invalid uid")
    if not 2 <= len(username) <= 4:
        raise ValueError("invalid username")

    return JsonResponse({"uid": uid, "user_name": username})


urlpatterns = [route_path("api", demo_post, ["POST"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.django_hello_world_demo_urlconf")
