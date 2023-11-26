from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import _pydanitc_adapter, field
from pait.app.tornado import pait

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


class DemoHandler(RequestHandler):
    @pait()
    def get(self, demo_model: DemoModel = field.Query.i(raw_return=True)) -> None:
        self.write(demo_model.dict())


class Demo1Handler(RequestHandler):
    @pait()
    def post(self, demo_model: DemoModel = field.Json.i(raw_return=True)) -> None:
        self.write(demo_model.dict())


app: Application = Application([(r"/api/demo", DemoHandler), (r"/api/demo1", Demo1Handler)])


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
