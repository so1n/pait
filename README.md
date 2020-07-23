## pait
Pait is a python api interface tool, which can also be called a python api interface type (type hint)


pait enables your python web framework to have type checking and parameter type conversion like [fastapi](https://fastapi.tiangolo.com/) (power by [pydantic](https://pydantic-docs.helpmanual.io/))

[了解如何实现类型转换和检查功能](http://so1n.me/2019/04/15/%E7%BB%99python%E6%8E%A5%E5%8F%A3%E5%8A%A0%E4%B8%8A%E4%B8%80%E5%B1%82%E7%B1%BB%E5%9E%8B%E6%A3%80/)
## Installation
```Bash
pip install pait
```
## Usage
### IDE Support
While pydantic will work well with any IDE out of the box.
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

Currently only supports `starlette` and `flask`(more python web frameworks will be supported in the future)

`starlette` use example:
```Python
import uvicorn

from typing import Optional
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

from pait.field import Body, Query
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
        other_model: PydanticOtherModel = Body()
):
    """Test Method:Post request, Pydantic Model and request"""
    print(request)
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return JSONResponse({'result': model.dict()})


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
    model: PydanticOtherModel = Query()
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
```

`flask` use example:
```Python
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


@app.route("/api", methods=['POST'])
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
```