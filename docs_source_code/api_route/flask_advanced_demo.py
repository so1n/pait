from flask import Flask
from flask.views import MethodView

from pait.app.flask import APIRoute, pait
from pait.field import Header, Json
from pait.model.tag import Tag

# User routes.
user_api_route = APIRoute(path="/user", tag=(Tag("api-route-user"),), group="user")


@user_api_route.get("/profile")
def get_profile(user_id: int = Header.i(alias="X-User-ID", description="User ID")) -> dict:
    """Get user profile"""
    return {"code": 0, "msg": "ok", "data": {"user_id": user_id, "name": "User Profile"}}


def login(username: str = Json.i(description="Username"), password: str = Json.i(description="Password")) -> dict:
    """User login"""
    return {"code": 0, "msg": "ok", "data": {"token": f"token_for_{username}"}}


# Add a route with add_api_route.
user_api_route.add_api_route(login, method=["POST"], path="/login")


# Order class-based view.
class OrderAPIView(MethodView):
    """Order management CBV"""

    def get(self, order_id: int = Header.i(alias="X-Order-ID", description="Order ID")) -> dict:
        """Get order details"""
        return {"code": 0, "msg": "ok", "data": {"order_id": order_id, "status": "completed"}}

    @pait()
    def post(
        self, total: float = Json.i(description="Order total"), items: list = Json.i(description="Order items")
    ) -> dict:
        """Create a new order"""
        return {"code": 0, "msg": "ok", "data": {"order_id": 12345, "total": total, "items": items}}


# Order routes.
order_api_route = APIRoute(path="/order", tag=(Tag("api-route-order"),), group="order")
order_api_route.add_cbv_route(OrderAPIView, path="/manage")


# Main route including sub routes.
main_api_route = APIRoute(path="/api/v1", tag=(Tag("api-route-v1"),)).include_sub_route(user_api_route, order_api_route)


def create_app() -> Flask:
    app = Flask(__name__)
    main_api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
