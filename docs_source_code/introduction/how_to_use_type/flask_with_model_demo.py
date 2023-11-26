from flask import Flask, Response, jsonify
from pydantic import BaseModel, Field

from pait import _pydanitc_adapter, field
from pait.app.flask import pait

if _pydanitc_adapter.is_v1:

    class DemoModel(BaseModel):
        uid: str = Field(max_length=6, min_length=6, regex="^u")
        name: str = Field(min_length=4, max_length=10)
        age: int = Field(ge=0, le=100)

else:

    class DemoModel(BaseModel):  # type: ignore
        uid: str = Field(max_length=6, min_length=6, pattern="^u")
        name: str = Field(min_length=4, max_length=10)
        age: int = Field(ge=0, le=100)


@pait()
def demo(demo_model: DemoModel = field.Query.i(raw_return=True)) -> Response:
    return jsonify(demo_model.dict())


@pait()
def demo1(demo_model: DemoModel = field.Json.i(raw_return=True)) -> Response:
    return jsonify(demo_model.dict())


app = Flask("demo")
app.add_url_rule("/api/demo", "demo", demo, methods=["GET"])
app.add_url_rule("/api/demo1", "demo1", demo1, methods=["POST"])


if __name__ == "__main__":
    app.run(port=8000)
