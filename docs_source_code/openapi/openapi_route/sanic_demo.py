from pydantic import BaseModel, Field
from sanic import HTTPResponse, Sanic, json

from pait.app.sanic import pait
from pait.field import Body
from pait.model.template import TemplateVar
from pait.openapi.doc_route import AddDocRoute


class UserModel(BaseModel):
    uid: int = Field(description="user id", gt=10, lt=1000, example=TemplateVar("uid"))
    user_name: str = Field(description="user name", min_length=2, max_length=4)


@pait()
async def demo_post(model: UserModel = Body.i()) -> HTTPResponse:
    return json({"result": model.dict()})


app = Sanic(name="demo")
app.add_route(demo_post, "/api", methods=["POST"])


if __name__ == "__main__":
    AddDocRoute(app)
    import uvicorn

    uvicorn.run(app)
