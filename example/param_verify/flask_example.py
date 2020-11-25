from typing import Optional

from flask import Flask, Request
from flask.views import MethodView

from pait.app.flask_pait import pait
from pait.exceptions import PaitException
from pait.field import Body, Depends, Header, Path, Query
from pait.model import PaitStatus
from pydantic import ValidationError
from pydantic import (
    conint,
    constr,
)

from example.param_verify.model import UserModel, UserOtherModel, SexEnum, TestPaitModel, demo_depend


app = Flask(__name__)


def api_exception(exc: Exception):
    return {'exc': str(exc)}


@app.route("/api/raise_tip", methods=['POST'])
@pait(author=('so1n', ), desc='test pait raise tip', status=PaitStatus.abandoned)
def test_raise_tip(
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
        content__type: str = Header(description='Content-Type')  # in flask, Content-Type's key is content_type
):
    """Test Method: error tip"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content__type})
    return return_dict


@app.route("/api/post", methods=['POST'])
@pait(author=('so1n', ), group='user', status=PaitStatus.release)
def test_post(
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
        content_type: str = Header(alias='Content-Type', description='Content-Type')
):
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return return_dict


@app.route("/api/depend", methods=['GET'])
@pait(author=('so1n', ), group='user', status=PaitStatus.release)
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
@pait(author=('so1n', ), group='user', status=PaitStatus.release)
def test_pait(
        uid: conint(gt=10, lt=1000) = Query(description='user id'),
        user_name: constr(min_length=2, max_length=4) = Query(description='user name'),
        email: Optional[str] = Query(default='example@xxx.com', description='user email'),
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


@app.route("/api/pait_model", methods=['GET'])
@pait(author=('so1n', ), status=PaitStatus.test)
def test_model(test_model: TestPaitModel):
    """Test Field"""
    return test_model.dict()


class TestCbv(MethodView):
    user_agent: str = Header(alias='user-agent', description='ua')  # remove key will raise error

    @pait(author=('so1n', ), group='user', status=PaitStatus.test)
    def get(
        self,
        uid: conint(gt=10, lt=1000) = Query(description='user id'),
        user_name: constr(min_length=2, max_length=4) = Query(description='user name'),
        email: Optional[str] = Query(default='example@xxx.com', description='email'),
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

    @pait(author=('so1n', ), desc='test cbv post method', group='user', status=PaitStatus.test)
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


if __name__ == "__main__":
    app.run(port=8000, debug=True)
