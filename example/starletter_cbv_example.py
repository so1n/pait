import uvicorn

from typing import Optional
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
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


class Homepage(HTTPEndpoint):
    content_type: str = Header(key='Content-Type')  # remove key will raise error

    @params_verify()
    async def get(
        self,
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

    @params_verify()
    async def post(
        self,
        model: PydanticModel = Body(),
        other_model: PydanticOtherModel = Body(),
    ):
        return_dict = model.dict()
        return_dict.update(other_model.dict())
        return_dict.update({'content_type': self.content_type})
        return JSONResponse({'result': return_dict})


routes = [
    Route("/api", Homepage),
]

app = Starlette(routes=routes)
uvicorn.run(app, log_level='debug')
