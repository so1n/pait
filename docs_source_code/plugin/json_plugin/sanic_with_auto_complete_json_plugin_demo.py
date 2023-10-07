from typing import List, Type

from pydantic import BaseModel, Field
from sanic import Request, Sanic

from pait.app.sanic import pait
from pait.app.sanic.plugin import AutoCompleteJsonRespPlugin
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


@pait(response_model_list=[AutoCompleteRespModel], plugin_list=[AutoCompleteJsonRespPlugin.build()])
async def demo(request: Request) -> dict:
    """Test json plugin by resp type is dict"""
    return {
        "code": 0,
        "msg": "",
        "data": {
            # "uid": 0,
            "image_list": [
                {"aaa": 10},
                {"aaa": "123"},
            ],
            "music_list": [
                {
                    "name": "music1",
                    "url": "http://music1.com",
                    "singer": "singer1",
                },
                {
                    # "name": "music1",
                    "url": "http://music1.com",
                    # "singer": "singer1",
                },
            ],
        },
    }


app = Sanic("demo")
app.add_route(demo, "/api/demo", methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
