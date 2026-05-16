import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait.app.django import pait

fake_db_dict: dict = {"u12345": "so1n"}


class GetUserDepend(object):
    user_name: str = field.Query.i()

    def __call__(self, token: str = field.Header.i()) -> str:
        if token not in fake_db_dict:
            raise RuntimeError(f"Can not found by token:{token}")
        user_name = fake_db_dict[token]
        if user_name != self.user_name:
            raise RuntimeError("The specified user could not be found through the token")
        return user_name


@pait()
def demo(token: str = field.Depends.i(GetUserDepend)) -> JsonResponse:
    return JsonResponse({"user": token})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.depend.django_with_class_depend_demo_urlconf")
