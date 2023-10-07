import datetime

from sanic import Sanic, json, response

from pait import field
from pait.app.sanic import pait


@pait()
async def demo(timestamp: datetime.datetime = field.Query.i()) -> response.HTTPResponse:
    return json({"time": timestamp.isoformat()})


app = Sanic(name="demo")
app.add_route(demo, "/api/demo", methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
