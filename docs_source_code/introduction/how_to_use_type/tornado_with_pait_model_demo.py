from uuid import uuid4

from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import _pydanitc_adapter, field
from pait.app.tornado import pait

if _pydanitc_adapter.is_v1:

    class DemoModel(BaseModel):
        uid: str = Field(..., max_length=6, min_length=6, regex="^u")
        name: str = Field(..., min_length=4, max_length=10)
        age: int = Field(..., ge=0, le=100)

        request_id: str = field.Header.i(default_factory=lambda: str(uuid4()))

else:

    class DemoModel(BaseModel):  # type: ignore
        uid: str = Field(..., max_length=6, min_length=6, pattern="^u")
        name: str = Field(..., min_length=4, max_length=10)
        age: int = Field(..., ge=0, le=100)

        request_id: str = field.Header.i(default_factory=lambda: str(uuid4()))


class DemoHandler(RequestHandler):
    @pait(default_field_class=field.Query)
    def get(self, demo_model: DemoModel) -> None:
        self.write(demo_model.dict())


class Demo1Handler(RequestHandler):
    @pait(default_field_class=field.Body)
    def post(self, demo_model: DemoModel) -> None:
        self.write(demo_model.dict())


app: Application = Application([(r"/api/demo", DemoHandler), (r"/api/demo1", Demo1Handler)])


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
