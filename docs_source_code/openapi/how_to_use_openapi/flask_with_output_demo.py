from typing import Any, Type

from any_api.openapi.to.markdown import Markdown
from flask import Flask, Response, jsonify
from pydantic import BaseModel, Field

from pait.app.flask import pait
from pait.field import Body
from pait.g import config
from pait.model.response import JsonResponseModel
from pait.openapi.openapi import OpenAPI


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel])
def demo_post(
    uid: int = Body.t(description="user id", gt=10, lt=1000),
    username: str = Body.t(description="user name", min_length=2, max_length=4),
) -> Response:
    return jsonify({"uid": uid, "user_name": username})


app = Flask("demo")
app.add_url_rule("/api", "demo", demo_post, methods=["POST"])


def my_serialization(content: str, **kwargs: Any) -> str:
    import json

    import yaml  # type: ignore

    return yaml.dump(json.loads(json.dumps(content, cls=config.json_encoder), **kwargs))


openapi_model = OpenAPI(app)

print("json", openapi_model.content())
print("yaml", openapi_model.content(serialization_callback=my_serialization))
for i18n_lang in ("zh-cn", "en"):
    print(f"{i18n_lang} md", Markdown(openapi_model, i18n_lang=i18n_lang).content)
