from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait
from pait.exceptions import TipException


async def api_exception(request: Request, exc: Exception) -> PlainTextResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return PlainTextResponse(str(exc))


@pait()
async def demo(demo_value: str = field.Query.t(default="123")) -> PlainTextResponse:
    return PlainTextResponse(demo_value)


@pait()
async def demo1(demo_value: str = field.Query.t()) -> PlainTextResponse:
    return PlainTextResponse(demo_value)


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
        Route("/api/demo1", demo1, methods=["GET"]),
    ]
)
app.add_exception_handler(Exception, api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
