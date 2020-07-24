from typing import Optional

from flask import Flask

from pait.field import Body, Query
from pait.web.flask import params_verify
from pydantic import (
    BaseModel,
    conint,
    constr,
)


class PydanticModel(BaseModel):
    uid: conint(gt=10, lt=1000)
    user_name: constr(min_length=2, max_length=4)


class PydanticOtherModel(BaseModel):
    age: conint(gt=1, lt=100)


app = Flask(__name__)


@app.route("/api1", methods=['POST'])
@params_verify()
def demo_post(
    model: PydanticModel = Body(),
    other_model: PydanticOtherModel = Body()
):
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return {'result': model.dict()}


@app.route("/api2", methods=['GET'])
@params_verify()
def demo_get2(
    model: PydanticModel = Query(),
    other_model: PydanticOtherModel = Query()
):
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return {'result': model.dict()}


@app.route("/api", methods=['GET'])
@params_verify()
def demo_get(
    uid: conint(gt=10, lt=1000) = Query(),
    user_name: constr(min_length=2, max_length=4) = Query(),
    email: Optional[str] = Query(default='example@xxx.com'),
    model: PydanticOtherModel = Query()
):
    """Text Pydantic Model and Field"""
    _dict = {
        'uid': uid,
        'user_name': user_name,
        'email': email,
        'age': model.age
    }
    return {'result': _dict}


app.run(port=8000)
