import datetime
from typing import Callable, Generator, Union

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait._pydanitc_adapter import is_v1
from pait.app.starlette import pait

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


@pait()
async def demo(timestamp: UnixDatetime = field.Query.i()) -> JSONResponse:
    return JSONResponse({"time": timestamp.isoformat()})


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
