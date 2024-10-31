from sanic import HTTPResponse, Sanic

from pait import field
from pait.app.sanic import pait


@pait()
async def demo(content_type: str = field.Header.t(alias="Content-Type")) -> HTTPResponse:
    return HTTPResponse(content_type)


app: Sanic = Sanic(name="demo", configure_logging=False)
app.add_route(demo, "/api/demo", methods={"GET"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
