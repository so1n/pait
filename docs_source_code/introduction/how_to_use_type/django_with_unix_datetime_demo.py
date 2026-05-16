import datetime
import os
import sys
from typing import Callable, Generator, Union

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait._pydanitc_adapter import is_v1
from pait.app.django import pait

if is_v1:

    class UnixDatetime(datetime.datetime):
        @classmethod
        def __get_validators__(cls) -> Generator[Callable, None, None]:
            yield cls.validate

        @classmethod
        def validate(cls, v: Union[int, str]) -> datetime.datetime:
            if isinstance(v, str):
                v = int(v)
            return datetime.datetime.fromtimestamp(v)

else:
    from pydantic import BeforeValidator
    from typing_extensions import Annotated

    def validate(v: Union[int, str]) -> datetime.datetime:
        if isinstance(v, str):
            v = int(v)
        return datetime.datetime.fromtimestamp(v)

    UnixDatetime = Annotated[datetime.datetime, BeforeValidator(validate)]  # type: ignore


@pait()
def demo(timestamp: UnixDatetime = field.Query.i()) -> JsonResponse:
    return JsonResponse({"time": timestamp.isoformat()})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(
        urlpatterns,
        "docs_source_code.introduction.how_to_use_type.django_with_unix_datetime_demo_urlconf",
    )
