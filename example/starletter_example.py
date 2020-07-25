import uvicorn

from typing import Optional
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

from pait.field import Body, Header, Query
from pait.web.starletter import params_verify
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


@params_verify()
async def demo_post(
        request: Request,
        model: PydanticModel = Body(),
        other_model: PydanticOtherModel = Body(),
        content_type: str = Header(key='Content-Type')  # remote key will get an error
):
    """Test Method:Post request, Pydantic Model and request"""
    print(request)
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return JSONResponse({'result': return_dict})


@params_verify()
async def demo_get2(
    model: PydanticModel = Query(),
    other_model: PydanticOtherModel = Query()
):
    """Test Method:Post request, Pydantic Model"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return JSONResponse({'result': return_dict})


@params_verify()
async def demo_get(
    uid: conint(gt=10, lt=1000) = Query(),
    user_name: constr(min_length=2, max_length=4) = Query(),
    email: Optional[str] = Query(default='example@xxx.com'),
    model: PydanticOtherModel = Query(),
):
    """Text Pydantic Model and Field"""
    _dict = {
        'uid': uid,
        'user_name': user_name,
        'email': email,
        'age': model.age
    }
    return JSONResponse({'result': _dict})


app = Starlette(
    routes=[
        Route('/api', demo_get, methods=['GET']),
        Route('/api1', demo_post, methods=['POST']),
        Route('/api2', demo_get2, methods=['GET']),
    ]
)


uvicorn.run(app)
