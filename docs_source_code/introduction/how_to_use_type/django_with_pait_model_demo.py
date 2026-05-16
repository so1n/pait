import os
import sys
from uuid import uuid4

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse
from pydantic import BaseModel, Field

from example.django_example.utils import route_path, run_urlpatterns
from pait import _pydanitc_adapter, field
from pait.app.django import pait

if _pydanitc_adapter.is_v1:

    class DemoModel(BaseModel):
        uid: str = Field(..., max_length=6, min_length=6, regex="^u")
        name: str = Field(..., min_length=4, max_length=10)
        age: int = Field(..., ge=0, le=100)
        request_id: str = field.Header.i(default_factory=lambda: str(uuid4()))

else:

    class DemoModel(BaseModel):  # type: ignore
        uid: str = Field(..., max_length=6, min_length=6, pattern="^u")
        name: str = Field(..., min_length=4, max_length=10)
        age: int = Field(..., ge=0, le=100)
        request_id: str = field.Header.i(default_factory=lambda: str(uuid4()))


@pait(default_field_class=field.Query)
def demo(demo_model: DemoModel) -> JsonResponse:
    return JsonResponse(demo_model.dict())


@pait(default_field_class=field.Body)
def demo1(demo_model: DemoModel) -> JsonResponse:
    return JsonResponse(demo_model.dict())


urlpatterns = [
    route_path("api/demo", demo, ["GET"], name="demo"),
    route_path("api/demo1", demo1, ["POST"], name="demo1"),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.introduction.how_to_use_type.django_with_pait_model_demo_urlconf")
