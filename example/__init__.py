"""
>>> curl "127.0.0.1:8000/api?uid=123&user_name=apple&age=-1"
{"error":"1 validation error for PydanticModel\nuser_name\n  ensure this value has at most 4 characters (type=value_error.any_str.max_length; limit_value=4)"}
>>> curl "127.0.0.1:8000/api?uid=123&user_name=appl&age=-1"
{"error":"1 validation error for PydanticOtherModel\nage\n  ensure this value is greater than 1 (type=value_error.number.not_gt; limit_value=1)"}
>>> curl "127.0.0.1:8000/api?uid=123&user_name=appl&age=1"
{"error":"1 validation error for PydanticOtherModel\nage\n  ensure this value is greater than 1 (type=value_error.number.not_gt; limit_value=1)"}
>>> curl "127.0.0.1:8000/api?uid=123&user_name=appl&age=2"
{"result":{"uid":123,"user_name":"appl","age":2}}
"""
import uvicorn

from starlette.applications import Starlette
from starlette.routing import Route

from pydantic import (
    BaseModel,
    conint,
    constr,
)

from pait import params_verify


class PydanticModel(BaseModel):
    uid: conint(gt=10, lt=1000)
    user_name: constr(min_length=2, max_length=4)


class PydanticOtherModel(BaseModel):
    age: conint(gt=1, lt=100)


@params_verify()
async def demo_post(request, model: PydanticModel) -> dict:
    return {'result': model.dict()}


@params_verify()
async def demo_get(request, model: PydanticModel, other_model: PydanticOtherModel) -> dict:
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return {'result': return_dict}


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
        Route('/api', demo_get, methods=['GET']),
    ]
)


uvicorn.run(app)
