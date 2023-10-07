import datetime
from typing import Callable, Generator, Union

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import field
from pait._pydanitc_adapter import is_v1
from pait.app.tornado import pait

if is_v1:

    class UnixDatetime(datetime.datetime):
        @classmethod
        def __get_validators__(cls) -> Generator[Callable, None, None]:
            yield cls.validate

        @classmethod
        def validate(cls, v: Union[int, str]) -> datetime.datetime:
            if isinstance(v, str):
                v = int(v)
            return datetime.datetime.fromtimestamp(v)

else:
    from pydantic import BeforeValidator
    from typing_extensions import Annotated

    def validate(v: Union[int, str]) -> datetime.datetime:
        if isinstance(v, str):
            v = int(v)
        return datetime.datetime.fromtimestamp(v)

    UnixDatetime = Annotated[datetime.datetime, BeforeValidator(validate)]  # type: ignore


class DemoHandler(RequestHandler):
    @pait()
    def get(self, timestamp: UnixDatetime = field.Query.i()) -> None:
        self.write({"time": timestamp.isoformat()})


app: Application = Application(
    [
        (r"/api/demo", DemoHandler),
    ]
)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
