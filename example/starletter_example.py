import uvicorn

from typing import Optional
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

from pait.exceptions import PaitException
from pait.field import Body, Depends, Header, Path, Query
from pait.app.starletter import params_verify, load_app
from pydantic import ValidationError
from pydantic import (
    conint,
    constr,
)

from example.model import UserModel, UserOtherModel, SexEnum, TestPaitModel, demo_depend


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({'exc': str(exc)})


@params_verify()
async def test_raise_tip(
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
        content_type: str = Header()
):
    """Test Method: error tip"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return JSONResponse(return_dict)


@params_verify()
async def test_post(
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
        content_type: str = Header(key='Content-Type')
):
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return JSONResponse(return_dict)


@params_verify()
async def test_depend(
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
    return JSONResponse(return_dict)


@params_verify()
async def test_get(
        uid: conint(gt=10, lt=1000) = Query(),
        user_name: constr(min_length=2, max_length=4) = Query(),
        email: Optional[str] = Query(default='example@xxx.com'),
        age: str = Path(),
        sex: SexEnum = Query()
):
    """Test Field"""
    _dict = {
        'uid': uid,
        'user_name': user_name,
        'email': email,
        'age': age,
        'sex': sex.value
    }
    return JSONResponse(_dict)


@params_verify()
async def test_pait_model(test_model: TestPaitModel):
    """Test Field"""
    return JSONResponse(test_model.dict())


class TestCbv(HTTPEndpoint):
    user_agent: str = Header(key='user-agent')  # remove key will raise error

    @params_verify()
    async def get(
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
            'age': model.age,
            'cbv_id': id(self)
        }
        return JSONResponse({'result': _dict})

    @params_verify()
    async def post(
        self,
        model: UserModel = Body(),
        other_model: UserOtherModel = Body(),
    ):
        return_dict = model.dict()
        return_dict.update(other_model.dict())
        return_dict.update({'user-agent': self.user_agent})
        return_dict.update({'cbv_id': id(self)})
        return JSONResponse({'result': return_dict})


app = Starlette(
    routes=[
        Route('/api/get/{age}', test_get, methods=['GET']),
        Route('/api/post', test_post, methods=['POST']),
        Route('/api/depend', test_depend, methods=['GET']),
        Route('/api/raise_tip', test_raise_tip, methods=['POST']),
        Route('/api/cbv', TestCbv),
        Route('/api/pait_model', test_pait_model, methods=['GET'])
    ]
)

load_app(app)
app.add_exception_handler(PaitException, api_exception)
app.add_exception_handler(ValidationError, api_exception)
uvicorn.run(app, log_level='debug')
