import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from pait.app.starlette import APIRoute
from pait.field import Json

api_route = APIRoute(path="/api")


async def greet(name: str = Json.i()) -> JSONResponse:
    return JSONResponse({"message": f"Hello {name}"})


api_route.add_api_route(greet, method=["POST"], path="/greet", desc="Greeting API")


def create_app() -> Starlette:
    app = Starlette()
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
