from uuid import uuid4

from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import _pydanitc_adapter, field
from pait.app.starlette import pait

if _pydanitc_adapter.is_v1:

    class DemoModel(BaseModel):
        uid: str = Field(..., max_length=6, min_length=6, regex="^u")
        name: str = Field(..., min_length=4, max_length=10)
        age: int = Field(..., ge=0, le=100)

        request_id: str = field.Header.i(default_factory=lambda: str(uuid4()))

else:

    class DemoModel(BaseModel):  # type: ignore
        uid: str = Field(..., max_length=6, min_length=6, pattern="^u")
        name: str = Field(..., min_length=4, max_length=10)
        age: int = Field(..., ge=0, le=100)

        request_id: str = field.Header.i(default_factory=lambda: str(uuid4()))


@pait(default_field_class=field.Query)
async def demo(demo_model: DemoModel) -> JSONResponse:
    return JSONResponse(demo_model.dict())


@pait(default_field_class=field.Body)
async def demo1(demo_model: DemoModel) -> JSONResponse:
    return JSONResponse(demo_model.dict())


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"]), Route("/api/demo1", demo1, methods=["POST"])])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
