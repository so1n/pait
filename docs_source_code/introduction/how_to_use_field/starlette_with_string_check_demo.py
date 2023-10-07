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
async def demo(demo_value: str = field.Query.i(min_length=6, max_length=6, regex="^u")) -> JSONResponse:
    return JSONResponse({"data": demo_value})


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)
app.add_exception_handler(Exception, api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
