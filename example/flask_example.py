from typing import Optional

from flask import Flask

from pait.field import Body, Header, Path, Query
from pait.web.flask import params_verify
from pydantic import (
    conint,
    constr,
)

from example.model import UserModel, UserOtherModel


app = Flask(__name__)


@app.route("/api1", methods=['POST'])
@params_verify()
def demo_post2(
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
        content_type: str = Header()
):
    """Test Method: error tip"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return return_dict


@app.route("/api", methods=['POST'])
@params_verify()
def demo_post1(
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
        content_type: str = Header(key='Content-Type')
):
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return return_dict


@app.route("/api1", methods=['GET'])
@params_verify()
def demo_get2(
        model: UserModel = Query(),
        other_model: UserOtherModel = Query(),
):
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return return_dict


@app.route("/api/<age>", methods=['GET'])
@params_verify()
def demo_get1(
        uid: conint(gt=10, lt=1000) = Query(),
        user_name: constr(min_length=2, max_length=4) = Query(),
        email: Optional[str] = Query(default='example@xxx.com'),
        age: str = Path()
):
    """Test Field"""
    return {
        'uid': uid,
        'user_name': user_name,
        'email': email,
        'age': age
    }


app.run(port=8000, debug=True)
