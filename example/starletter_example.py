import uvicorn

from typing import Optional
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

from pait.field import Body, Depends, Header, Path, Query
from pait.web.starletter import params_verify
from pydantic import (
    conint,
    constr,
)

from example.model import UserModel, UserOtherModel


def demo_sub_depend(user_agent: str = Header(key='user-agent')):
    print('sub_depend', user_agent)
    return user_agent


def demo_depend(user_agent: str = Depends(demo_sub_depend)):
    print('depend', user_agent)
    return user_agent


@params_verify()
async def demo_post2(
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
async def demo_post1(
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
async def demo_get2(
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
    return JSONResponse(return_dict)


from enum import Enum


class SexEnum(Enum):
    man: str = 'man'
    woman: str = 'woman'


@params_verify()
async def demo_get1(
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


app = Starlette(
    routes=[
        Route('/api/{age}', demo_get1, methods=['GET']),
        Route('/api', demo_post1, methods=['POST']),
        Route('/api1', demo_get2, methods=['GET']),
        Route('/api1', demo_post2, methods=['POST']),

    ]
)

uvicorn.run(app, log_level='debug')
