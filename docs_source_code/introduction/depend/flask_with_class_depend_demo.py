from flask import Flask, Response, jsonify

from pait import field
from pait.app.flask import pait
from pait.exceptions import TipException


def api_exception(exc: Exception) -> Response:
    if isinstance(exc, TipException):
        exc = exc.exc
    return jsonify({"data": str(exc)})


fake_db_dict: dict = {"u12345": "so1n"}


class GetUserDepend(object):
    user_name: str = field.Query.i()

    def __call__(self, token: str = field.Header.i()) -> str:
        if token not in fake_db_dict:
            raise RuntimeError(f"Can not found by token:{token}")
        user_name = fake_db_dict[token]
        if user_name != self.user_name:
            raise RuntimeError("The specified user could not be found through the token")
        return user_name


@pait()
def demo(token: str = field.Depends.i(GetUserDepend)) -> dict:
    return {"user": token}


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
