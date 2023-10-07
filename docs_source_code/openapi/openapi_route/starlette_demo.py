from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body
from pait.model.template import TemplateVar
from pait.openapi.doc_route import AddDocRoute


class UserModel(BaseModel):
    uid: int = Field(description="user id", gt=10, lt=1000, example=TemplateVar("uid"))
    user_name: str = Field(description="user name", min_length=2, max_length=4)


@pait()
async def demo_post(model: UserModel = Body.i()) -> JSONResponse:
    return JSONResponse({"result": model.dict()})


app = Starlette(routes=[Route("/api", demo_post, methods=["POST"])])


if __name__ == "__main__":
    AddDocRoute(app)
    import uvicorn

    uvicorn.run(app)
