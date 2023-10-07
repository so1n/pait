from typing import List

from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.field import Query
from pait.model.response import BaseResponseModel
from pait.openapi.doc_route import AddDocRoute


class MyJsonResponseModel(BaseResponseModel):
    class ResponseModel(BaseModel):
        class UserModel(BaseModel):
            name: str = Field(..., example="so1n")
            uid: int = Query.t(description="user id", gt=10, lt=1000)
            age: int = Field(..., gt=0)

        code: int = Field(..., ge=0)
        msg: str = Field(...)
        data: List[UserModel]

    class HeaderModel(BaseModel):
        x_token: str = Field(..., alias="X-Token")
        content_type: str = Field(..., alias="Content-Type")

    response_data = ResponseModel
    description = "demo json response"
    media_type = "application/json; charset=utf-8"
    header = HeaderModel
    status_code = (200, 201, 404)


class DemoHandler(RequestHandler):
    @pait(response_model_list=[MyJsonResponseModel])
    def get(
        self,
        uid: int = Query.t(description="user id", gt=10, lt=1000),
        age: int = Query.t(description="age", gt=0),
        username: str = Query.t(description="user name", min_length=2, max_length=4),
    ) -> None:
        self.write({"code": 0, "msg": "", "data": [{"name": username, "uid": uid, "age": age}]})
        self.add_header("X-Token", "12345")
        self.set_header("Content-Type", "application/json; charset=utf-8")


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
