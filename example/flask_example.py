from typing import Optional

from flask import Flask, Request
from flask.views import MethodView

from pait.exceptions import PaitException
from pait.field import Body, Depends, Header, Path, Query
from pait.web.flask import params_verify
from pydantic import ValidationError
from pydantic import (
    conint,
    constr,
)

from example.model import UserModel, UserOtherModel, SexEnum, demo_depend


app = Flask(__name__)


def api_exception(exc: Exception):
    return {'exc': str(exc)}


@app.route("/api/raise_tip", methods=['POST'])
@params_verify()
def test_raise_tip(
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
        content_type: str = Header()
):
    """Test Method: error tip"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return return_dict


@app.route("/api/post", methods=['POST'])
@params_verify()
def test_post(
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
        content_type: str = Header(key='Content-Type')
):
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return return_dict


@app.route("/api/depend", methods=['GET'])
@params_verify()
def demo_get2test_depend(
        request: Request,
        model: UserModel = Query(),
        other_model: UserOtherModel = Query(),
        user_agent: str = Depends(demo_depend)
):
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, 'Not found request'
    print(user_agent)
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'user_agent': user_agent})
    return return_dict


@app.route("/api/get/<age>", methods=['GET'])
@params_verify()
def test_gettest_get(
        uid: conint(gt=10, lt=1000) = Query(),
        user_name: constr(min_length=2, max_length=4) = Query(),
        email: Optional[str] = Query(default='example@xxx.com'),
        age: str = Path(),
        sex: SexEnum = Query()
):
    """Test Field"""
    return {
        'uid': uid,
        'user_name': user_name,
        'email': email,
        'age': age,
        'sex': sex.value
    }


class TestCbv(MethodView):
    user_agent: str = Header(key='user-agent')  # remove key will raise error

    @params_verify()
    def get(
        self,
        uid: conint(gt=10, lt=1000) = Query(),
        user_name: constr(min_length=2, max_length=4) = Query(),
        email: Optional[str] = Query(default='example@xxx.com'),
        model: UserOtherModel = Query(),
    ):
        """Text Pydantic Model and Field"""
        _dict = {
            'uid': uid,
            'user_name': user_name,
            'email': email,
            'age': model.age
        }
        return {'result': _dict}

    @params_verify()
    def post(
        self,
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
    ):
        return_dict = model.dict()
        return_dict.update(other_model.dict())
        return_dict.update({'content_type': self.user_agent})
        return {'result': return_dict}


app.add_url_rule('/api/cbv', view_func=TestCbv.as_view('test_cbv'))
app.errorhandler(PaitException)(api_exception)
app.errorhandler(ValidationError)(api_exception)
app.run(port=8000, debug=True)
