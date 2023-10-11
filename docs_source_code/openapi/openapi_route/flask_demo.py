from flask import Flask, Response, jsonify
from pydantic import BaseModel, Field

from pait import _pydanitc_adapter
from pait.app.flask import pait
from pait.field import Body
from pait.model.template import TemplateVar
from pait.openapi.doc_route import AddDocRoute

if _pydanitc_adapter.is_v1:

    class UserModel(BaseModel):
        uid: int = Field(description="user id", gt=10, lt=1000, example=TemplateVar("uid"))
        user_name: str = Field(description="user name", min_length=2, max_length=4)

else:

    class UserModel(BaseModel):  # type: ignore[no-redef]
        uid: int = Field(
            description="user id", gt=10, lt=1000, json_schema_extra=lambda v: v.update(example=TemplateVar("uid"))
        )
        user_name: str = Field(description="user name", min_length=2, max_length=4)


@pait()
def demo_post(model: UserModel = Body.i()) -> Response:
    return jsonify({"result": model.dict()})


app = Flask("demo")
app.add_url_rule("/api", "demo", demo_post, methods=["POST"])


if __name__ == "__main__":
    AddDocRoute(app)
    app.run(port=8000)
