from typing import Type

from flask import Flask, Response, jsonify
from pydantic import BaseModel, Field

from pait.app.flask import pait
from pait.field import Json
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel])
def demo_post(
    uid: int = Json.t(description="user id", gt=10, lt=1000),
    username: str = Json.t(description="user name", min_length=2, max_length=4),
) -> Response:
    return jsonify({"uid": uid, "user_name": username})


app = Flask("demo")
app.add_url_rule("/api", "demo", demo_post, methods=["POST"])
AddDocRoute(app)


if __name__ == "__main__":
    app.run(port=8000)
