import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait.app.django import pait

fake_db_dict: dict = {"u12345": "so1n"}


def get_user_by_token(token: str = field.Header.i()) -> str:
    if token not in fake_db_dict:
        raise RuntimeError(f"Can not found by token:{token}")
    return fake_db_dict[token]


@pait()
def demo(token: str = field.Depends.i(get_user_by_token)) -> JsonResponse:
    return JsonResponse({"user": token})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.depend.django_with_depend_demo_urlconf")
