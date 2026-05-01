from flask import Flask
from flask.views import MethodView

from pait.app.flask import APIRoute, pait
from pait.field import Header, Json

api_route = APIRoute(path="/api")


class UserAPIView(MethodView):
    def get(self, user_id: int = Header.i(alias="X-User-ID")) -> dict:
        return {"user_id": user_id}

    @pait()
    def post(self, name: str = Json.i()) -> dict:
        return {"created": {"name": name}}


api_route.add_cbv_route(UserAPIView, path="/users")


def create_app() -> Flask:
    app = Flask(__name__)
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
