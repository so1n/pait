from typing import Type

from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.app.tornado.plugin.mock_response import MockPlugin
from pait.field import Json
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field(example=999)
        username: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


class DemoHandler(RequestHandler):
    @pait(response_model_list=[DemoResponseModel], plugin_list=[MockPlugin.build()])
    async def post(
        self,
        uid: int = Json.t(description="user id", gt=10, lt=1000),
        username: str = Json.t(description="user name", min_length=2, max_length=4),
    ) -> None:
        pass


app: Application = Application([(r"/api", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
