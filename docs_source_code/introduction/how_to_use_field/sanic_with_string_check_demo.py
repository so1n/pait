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
async def demo(demo_value: str = field.Query.i(min_length=6, max_length=6, regex="^u")) -> HTTPResponse:
    return json({"data": demo_value})


app: Sanic = Sanic(name="demo", configure_logging=False)
app.add_route(demo, "/api/demo", methods={"GET"})
app.exception(Exception)(api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
