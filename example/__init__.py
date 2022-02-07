import datetime
from typing import Callable, Generator, Union

import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


class UnixDatetime(datetime.datetime):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Union[int, str]) -> datetime.datetime:
        if not isinstance(v, int):
            v = int(v)
        return datetime.datetime.fromtimestamp(v)


@pait()
async def demo(timestamp: UnixDatetime = field.Query.i()) -> JSONResponse:
    return JSONResponse({"time": timestamp.isoformat()})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])


uvicorn.run(app)
