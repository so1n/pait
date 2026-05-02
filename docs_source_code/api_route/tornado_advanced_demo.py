import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler

from pait.app.tornado import APIRoute, pait
from pait.field import Header, Json
from pait.model.tag import Tag

user_api_route = APIRoute(path="/user", tag=(Tag("api-route-user"),), group="user")


@user_api_route.get("/profile")
def get_profile(
    request: tornado.web.RequestHandler, user_id: int = Header.i(alias="X-User-ID", description="User ID")
) -> None:
    """Get user profile"""
    request.write({"code": 0, "msg": "ok", "data": {"user_id": user_id, "name": "User Profile"}})


def login(
    request: tornado.web.RequestHandler,
    username: str = Json.i(description="Username"),
    password: str = Json.i(description="Password"),
) -> None:
    """User login"""
    request.write({"code": 0, "msg": "ok", "data": {"token": f"token_for_{username}"}})


user_api_route.add_api_route(login, method=["POST"], path="/login")


class OrderAPIView(RequestHandler):
    """Order management CBV"""

    def get(self, order_id: int = Header.i(alias="X-Order-ID", description="Order ID")) -> None:
        """Get order details"""
        self.write({"code": 0, "msg": "ok", "data": {"order_id": order_id, "status": "completed"}})

    @pait()
    def post(
        self, total: float = Json.i(description="Order total"), items: list = Json.i(description="Order items")
    ) -> None:
        """Create a new order"""
        self.write({"code": 0, "msg": "ok", "data": {"order_id": 12345, "total": total, "items": items}})


order_api_route = APIRoute(path="/order", tag=(Tag("api-route-order"),), group="order")
order_api_route.add_cbv_route(OrderAPIView, path="/manage")

main_api_route = APIRoute(path="/api/v1", tag=(Tag("api-route-v1"),)).include_sub_route(user_api_route, order_api_route)


def make_app():
    app = tornado.web.Application()
    main_api_route.inject(app)
    return app


app = make_app()


if __name__ == "__main__":
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
