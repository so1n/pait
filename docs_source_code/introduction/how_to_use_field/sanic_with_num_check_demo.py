from pydantic import ValidationError
from sanic import HTTPResponse, Request, Sanic, json

from pait import field
from pait.app.sanic import pait
from pait.exceptions import TipException


async def api_exception(request: Request, exc: Exception) -> HTTPResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return json({"data": exc.errors()})
    return json({"data": str(exc)})


@pait()
async def demo(
    demo_value1: int = field.Query.i(gt=1, lt=10),
    demo_value2: int = field.Query.i(ge=1, le=1),
    demo_value3: int = field.Query.i(multiple_of=3),
) -> HTTPResponse:
    return json({"data": [demo_value1, demo_value2, demo_value3]})


app: Sanic = Sanic(name="demo", configure_logging=False)
app.add_route(demo, "/api/demo", methods={"GET"})
app.exception(Exception)(api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
