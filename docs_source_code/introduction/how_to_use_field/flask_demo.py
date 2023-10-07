from enum import Enum
from typing import List, Optional

from flask import Flask

from pait.app.flask import pait
from pait.field import Cookie, Form, MultiForm, MultiQuery, Path, Query


class SexEnum(str, Enum):
    man: str = "man"
    woman: str = "woman"


@pait()
def demo_route(
    a: str = Form.t(description="form data"),
    b: str = Form.t(description="form data"),
    c: List[str] = MultiForm.t(description="form data"),
    cookie: dict = Cookie.t(raw_return=True, description="cookie"),
    multi_user_name: List[str] = MultiQuery.t(description="user name", min_length=2, max_length=4),
    age: int = Path.t(description="age", gt=1, lt=100),
    uid: int = Query.t(description="user id", gt=10, lt=1000),
    user_name: str = Query.t(description="user name", min_length=2, max_length=4),
    email: Optional[str] = Query.t(default="example@xxx.com", description="user email"),
    sex: SexEnum = Query.t(description="sex"),
) -> dict:
    return {
        "code": 0,
        "msg": "",
        "data": {
            "form_a": a,
            "form_b": b,
            "form_c": c,
            "cookie": cookie,
            "multi_user_name": multi_user_name,
            "age": age,
            "uid": uid,
            "user_name": user_name,
            "email": email,
            "sex": sex,
        },
    }


app = Flask("demo")
app.add_url_rule("/api/demo/<age>", "demo", demo_route, methods=["POST"])


if __name__ == "__main__":
    app.run(port=8000)
