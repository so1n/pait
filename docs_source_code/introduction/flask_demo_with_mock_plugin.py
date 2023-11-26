from typing import Type

from flask import Flask, Response
from pydantic import BaseModel, Field

from pait.app.flask import pait
from pait.app.flask.plugin.mock_response import MockPlugin
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
def demo_post(  # type: ignore
    uid: int = Json.t(description="user id", gt=10, lt=1000),
    username: str = Json.t(description="user name", min_length=2, max_length=4),
) -> Response:
    pass


app = Flask("demo")
app.add_url_rule("/api", "demo", demo_post, methods=["POST"])
AddDocRoute(app)


if __name__ == "__main__":
    app.run(port=8000)
