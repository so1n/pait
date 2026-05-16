import os
import sys
from typing import List, Type

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from pydantic import BaseModel, Field

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.app.django.plugin import AutoCompleteJsonRespPlugin, UnifiedResponsePlugin
from pait.model.response import JsonResponseModel


class AutoCompleteRespModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        class DataModel(BaseModel):
            class MusicModel(BaseModel):
                name: str = Field("")
                url: str = Field()
                singer: str = Field("")

            uid: int = Field(100, description="user id", gt=10, lt=1000)
            music_list: List[MusicModel] = Field(description="music list")
            image_list: List[dict] = Field(description="music list")

        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


@pait(
    response_model_list=[AutoCompleteRespModel],
    plugin_list=[UnifiedResponsePlugin.build(), AutoCompleteJsonRespPlugin.build()],
)
def demo() -> dict:
    return {
        "code": 0,
        "msg": "",
        "data": {
            "image_list": [{"aaa": 10}, {"aaa": "123"}],
            "music_list": [
                {"name": "music1", "url": "http://music1.com", "singer": "singer1"},
                {"url": "http://music1.com"},
            ],
        },
    }


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(
        urlpatterns,
        "docs_source_code.plugin.json_plugin.django_with_auto_complete_json_plugin_demo_urlconf",
    )
