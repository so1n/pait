import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from pait.app.starlette import APIRoute, pait
from pait.field import Header, Json

api_route = APIRoute(path="/api")


class UserAPIView(HTTPEndpoint):
    async def get(self, user_id: int = Header.i(alias="X-User-ID")) -> JSONResponse:
        return JSONResponse({"user_id": user_id})

    @pait()
    async def post(self, name: str = Json.i()) -> JSONResponse:
        return JSONResponse({"created": {"name": name}})


api_route.add_cbv_route(UserAPIView, path="/users")


def create_app() -> Starlette:
    app = Starlette()
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
