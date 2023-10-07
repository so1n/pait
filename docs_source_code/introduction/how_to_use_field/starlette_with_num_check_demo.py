from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait
from pait.exceptions import TipException


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(
    demo_value1: int = field.Query.i(gt=1, lt=10),
    demo_value2: int = field.Query.i(ge=1, le=1),
    demo_value3: int = field.Query.i(multiple_of=3),
) -> JSONResponse:
    return JSONResponse({"data": [demo_value1, demo_value2, demo_value3]})


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)
app.add_exception_handler(Exception, api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
