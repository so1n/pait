from sanic import Sanic
from sanic.response import json
from sanic.views import HTTPMethodView

from pait.app.sanic import APIRoute, pait
from pait.field import Header, Json
from pait.model.tag import Tag

user_api_route = APIRoute(path="/user", tag=(Tag("api-route-user"),), group="user")


@user_api_route.get("/profile")
async def get_profile(user_id: int = Header.i(alias="X-User-ID", description="User ID")):
    """Get user profile"""
    return json({"code": 0, "msg": "ok", "data": {"user_id": user_id, "name": "User Profile"}})


async def login(username: str = Json.i(description="Username"), password: str = Json.i(description="Password")):
    """User login"""
    return json({"code": 0, "msg": "ok", "data": {"token": f"token_for_{username}"}})


user_api_route.add_api_route(login, method=["POST"], path="/login")


class OrderAPIView(HTTPMethodView):
    """Order management CBV"""

    async def get(self, order_id: int = Header.i(alias="X-Order-ID", description="Order ID")):
        """Get order details"""
        return json({"code": 0, "msg": "ok", "data": {"order_id": order_id, "status": "completed"}})

    @pait()
    async def post(
        self,
        total: float = Json.i(description="Order total"),
        items: list = Json.i(description="Order items"),
    ):
        """Create a new order"""
        return json({"code": 0, "msg": "ok", "data": {"order_id": 12345, "total": total, "items": items}})


order_api_route = APIRoute(path="/order", tag=(Tag("api-route-order"),), group="order")
order_api_route.add_cbv_route(OrderAPIView, path="/manage")

main_api_route = APIRoute(path="/api/v1", tag=(Tag("api-route-v1"),)).include_sub_route(user_api_route, order_api_route)


def create_app() -> Sanic:
    app = Sanic("api_route_advanced_demo")
    main_api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
