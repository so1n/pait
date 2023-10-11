from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import _pydanitc_adapter
from pait.app.tornado import pait
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


class DemoHandler(RequestHandler):
    @pait()
    async def post(self, model: UserModel = Body.i()) -> None:
        self.write({"result": model.dict()})


app: Application = Application([(r"/api", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
