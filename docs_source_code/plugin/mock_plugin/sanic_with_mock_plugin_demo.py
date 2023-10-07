from typing import List, Type

from pydantic import BaseModel, Field
from sanic import Sanic

from pait.app.sanic import pait
from pait.app.sanic.plugin import MockPlugin
from pait.field import Query
from pait.model.response import JsonResponseModel


class UserSuccessRespModel2(JsonResponseModel):
    class ResponseModel(BaseModel):
        class DataModel(BaseModel):
            uid: int = Field(description="user id", gt=10, lt=1000, example=666)
            user_name: str = Field(example="mock_name", description="user name", min_length=2, max_length=10)
            multi_user_name: List[str] = Field(
                example=["mock_name"], description="user name", min_length=1, max_length=10
            )
            age: int = Field(example=99, description="age", gt=1, lt=100)
            email: str = Field(example="example@so1n.me", description="user email")

        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[UserSuccessRespModel2], plugin_list=[MockPlugin.build()])
async def demo(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: str = Query.i(default="example@xxx.com", description="user email"),
) -> dict:
    return {}


app = Sanic("demo")
app.add_route(demo, "/api/demo", methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
