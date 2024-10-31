from typing import Type

from pydantic import BaseModel, Field
from sanic.app import Sanic
from sanic.response import HTTPResponse

from pait.app.sanic import pait
from pait.app.sanic.plugin.mock_response import MockPlugin
from pait.field import Json
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field(example=999)
        username: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel], plugin_list=[MockPlugin.build()])
async def demo_post(  # type: ignore[empty-body]
    uid: int = Json.t(description="user id", gt=10, lt=1000),
    username: str = Json.t(description="user name", min_length=2, max_length=4),
) -> HTTPResponse:
    pass


app = Sanic(name="demo", configure_logging=False)
app.add_route(demo_post, "/api", methods=["POST"])
AddDocRoute(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
