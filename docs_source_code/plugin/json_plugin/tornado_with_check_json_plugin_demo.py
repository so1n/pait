from typing import Type

from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.app.tornado.plugin import CheckJsonRespPlugin
from pait.exceptions import TipException
from pait.field import Query
from pait.model.response import JsonResponseModel


class UserSuccessRespModel3(JsonResponseModel):
    class ResponseModel(BaseModel):  # type: ignore
        class DataModel(BaseModel):
            uid: int = Field(description="user id", gt=10, lt=1000)
            user_name: str = Field(description="user name", min_length=2, max_length=4)
            age: int = Field(description="age", gt=1, lt=100)
            email: str = Field(description="user email")

        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


class _Handler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        if isinstance(exc, TipException):
            exc = exc.exc

        self.write({"data": str(exc)})
        self.finish()


class DemoHandler(_Handler):
    @pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
    async def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        email: str = Query.i(default="example@xxx.com", description="user email"),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        age: int = Query.i(description="age", gt=1, lt=100),
        display_age: int = Query.i(0, description="display_age"),
    ) -> None:
        return_dict: dict = {
            "code": 0,
            "msg": "",
            "data": {
                "uid": uid,
                "user_name": user_name,
                "email": email,
            },
        }
        if display_age == 1:
            return_dict["data"]["age"] = age
        self.write(return_dict)


app: Application = Application([(r"/api/demo", DemoHandler)])


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
