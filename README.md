## pait
Pait is a python api interface tool, which can also be called a python api interface type (type hint)

pait enables your python web framework to have type checking and parameter type conversion like [fastapi](https://fastapi.tiangolo.com/) (power by [pydantic](https://pydantic-docs.helpmanual.io/))


[了解如何实现类型转换和检查功能](http://so1n.me/2019/04/15/%E7%BB%99python%E6%8E%A5%E5%8F%A3%E5%8A%A0%E4%B8%8A%E4%B8%80%E5%B1%82%E7%B1%BB%E5%9E%8B%E6%A3%80/)
## Installation
```Bash
pip install pait
```
## Usage
### Use in route handle
A simple starletter route handler example:
```Python
import uvicorn

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse


async def demo_post(request: Request):
    return JSONResponse({'result': await request.json()})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)


uvicorn.run(app)
```
use pait in starletter route handler:
```Python
import uvicorn

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

# import from pait and pydantic
from pait.field import Body, Header, Query
from pait.web.starletter import params_verify
from pydantic import (
    BaseModel,
    conint,
    constr,
)


# create Pydantic.BaseModel
class PydanticModel(BaseModel):
    uid: conint(gt=10, lt=1000)
    user_name: constr(min_length=2, max_length=4)


# use params_verify in route handle
@params_verify()
async def demo_post(
    # pait knows to get the body data from the request by 'Body' 
    # and assign it to the Pydantic model
    model: PydanticModel = Body()  
):
    # replace body data to dict
    return JSONResponse({'result': model.dict()})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)


uvicorn.run(app)
```
## Field
- Field.Body: get body from request body data
- Field.Cookie: get cookie from header.cookie
- Field.File: get file object from request file
- Field.Form: get form from request form data
- Field.Header: get header from request header

`pait` will automatically use the variable name as the key and get the value from the body, for example:
```Python
@params_verify()
async def demo_post(
    # get uid from request body data
    uid: int = Body()  
):
    pass
```
If the variable name does not conform to the Python variable naming standard, can use`Field.Body(key=key_name)
```Python
@params_verify()
async def demo_post(
    # get uid from request body data
    uid: int = Body(),
    # get Content-Type from header
    content_type: str = Header(key='Content-Type')
):
    pass
```
`Pait` not return the request object, sometimes you may need the request object, you can write the request variable just like using the original web framework (must use TypeHint)
```Python
from starlette.requests import Request


@params_verify()
async def demo_post(
    request: Requests,
    # get uid from request body data
    uid: int = Body()  
):
    pass
```
## Other
### Error Tip
When you use pait incorrectly, pait will indicate in the exception the file path and line number of the function.
If you need more information, can set the log level to debug to get more detailed information

### How to used in other web framework?
If the web framework is not supported, which you are using.
Can be modified sync web framework according to [pait.web.flask](https://github.com/so1n/pait/blob/master/pait/web/flask.py)
Can be modified async web framework according to [pait.web.starletter](https://github.com/so1n/pait/blob/master/pait/web/starletter.py)
### IDE Support
While pydantic will work well with any IDE out of the box.
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

### Full example
Currently only supports `starlette` and `flask`(more python web frameworks will be supported in the future)

`starlette` use example:
```Python
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
        content_type: str = Header()
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
```

`flask` use example:
```Python
from typing import Optional

from flask import Flask

from pait.field import Body, Header, Query
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
    other_model: PydanticOtherModel = Body(),
    content_type: str = Header(key='Content-Type')
):
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({'content_type': content_type})
    return {'result': return_dict}


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