import datetime

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


@pait()
async def demo(timestamp: datetime.datetime = field.Query.i()) -> JSONResponse:
    return JSONResponse({"time": timestamp.isoformat()})


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
