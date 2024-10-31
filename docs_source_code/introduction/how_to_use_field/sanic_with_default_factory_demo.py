import datetime
import uuid

from sanic import HTTPResponse, Request, Sanic

from pait import field
from pait.app.sanic import pait
from pait.exceptions import TipException


async def api_exception(request: Request, exc: Exception) -> HTTPResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return HTTPResponse(str(exc))


@pait()
async def demo(demo_value: datetime.datetime = field.Query.t(default_factory=datetime.datetime.now)) -> HTTPResponse:
    return HTTPResponse(str(demo_value))


@pait()
async def demo1(demo_value: str = field.Query.t(default_factory=lambda: uuid.uuid4().hex)) -> HTTPResponse:
    return HTTPResponse(demo_value)


app: Sanic = Sanic(name="demo", configure_logging=False)
app.add_route(demo, "/api/demo", methods={"GET"})
app.add_route(demo1, "/api/demo1", methods={"GET"})
app.exception(Exception)(api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
