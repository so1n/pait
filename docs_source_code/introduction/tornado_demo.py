from typing import Type

from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.field import Body
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


class DemoHandler(RequestHandler):
    @pait(response_model_list=[DemoResponseModel])
    def post(
        self,
        uid: int = Body.t(description="user id", gt=10, lt=1000),
        username: str = Body.t(description="user name", min_length=2, max_length=4),
    ) -> None:
        self.write({"uid": uid, "user_name": username})


app: Application = Application([(r"/api", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
