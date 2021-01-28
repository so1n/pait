# pait
Pait is a python api interface tool, which can also be called a python api interface type (type hint)

pait enables your python web framework to have type checking and parameter type conversion like [fastapi](https://fastapi.tiangolo.com/) (power by [pydantic](https://pydantic-docs.helpmanual.io/))

[目前我正在学习英语中,英语文档可能比较难懂,可以参考中文说明](https://github.com/so1n/pait/blob/master/README_ZH.md)
# Installation
```Bash
pip install pait
```
# Usage

## 1.type checking and parameter type conversion
### 1.1Use in route handle
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
from pait.app.starlette import pait
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
@pait()
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
It can be seen that you only need to add a `params_verify` decorator to the routing function, and change the parameter of `demo_post` to `model: PydanticModel = Body()`.
Through `Body`, pait knows that it needs to get the body data from the post request.Pait knows that it needs to get the body data from the post request through `Body`. After that, pait converts and restricts the obtained data according to `conint(gt=10, lt=1000)` and assigns it to `PydanticModel`.Users only need to call `model` like using `Pydantic` to get the data.

This is just a simple demo. The above parameters only use one writing method. The two writing methods and uses supported by pait will be introduced below.

### 1.2Parameter expression supported by pait
For the convenience of users, pait supports two parameter expressions: model and type:
- model
The characteristic of the model is that the parameter type hints is a class inherited from `pydantic.BaseModel`.Pait will pass the value from the field to the model and perform type checksum conversion.The user only needs to call it like the method of `pydantic.BaseModel`.At this time, the `Field` filled by the user can use the `key`, `default`, and `fix_key` parameters during initialization, but pait will only use the `fix_key`. 
    ```Python
    model: PydanticModel = Body() 
    ```
- type
The characteristic of type is that the type hint parameter can be the python type, class (including Enum), typing value and the type value of `pydantic`. pait will convert all the parameters (about type) of the function to `pydantic.BaseModel`.Immediately afterwards, `pydantic.BaseModel` performs type check and type conversion and re-assigns the value to each parameter. At this time, the pait will call the `key`, `default`, and `fix_key` that were filled in when the user initialized the `Field`
    ```Python
    user_agent: str = Header(key='user-agent', default='not_set_ua')
    ```
### 1.3Field
Before introducing the Field function, please see the following example,`pait` will automatically use the variable name as the key and get the value from the body, for example:
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

The body of the field is used in the example. In addition to the body, pait also supports a variety of fields. Pait knows what type of data the user needs to obtain through the field. There are currently two types of fields, one is ordinary field, and the other is dependency injection Type field.

Ordinary field initialization parameters are `key`, `default`, and `fix_key`:
- key (only used for type writing)
In general, when the field is Field.Header, pait will get the header data of the current request, and use the parameter name key to get the data in the header, but the key naming method of the header is incompatible with the python variable naming, which will cause pait The corresponding data cannot be obtained.
Through the following example, after assigning the real key to the initialized key parameter, pait will preferentially select the key we assigned to get the corresponding value in the header
    ```Python
    user_agent: str = Header(key='user-agent', default='not_set_ua')
    ```
- default (only used for type writing)
  default value, When pait cannot get the desired data, it will directly quote the initialized default value
- fix_key
  In addition to using the key parameter to resolve the naming conflict between the key name and the python variable, you can also use `fix_key=True` to automatically resolve the naming conflict. This method is also the only solution to the model's naming conflict.


Field is divided into simple field and dependency injection field
There are many simple types, currently there are:
- Field.Body   gets the json data of the current request
- Field.Cookie gets the cookie data of the current request
- Field.File   gets the current request file data, and will return different file object types according to different web frameworks
- Field.Form   gets the current request form data
- Field.Header gets the current request header data
- Field.Path   gets the current request path data(for example url:/api/{version}/test, pait will get version value)
- Field.Query  gets the current request url param data


There is currently only one dependency injection field, and because the existence of model writing can serve as a partial dependency injection function, the dependency injection field function is relatively simple and only supports the execution of user functions when receiving requests. Generally used for interface verification or routing Check before function

## 2.requests object
After using `Pait`, the proportion of the number of times the requests object is used will decrease, so `pait` does not return the requests object. If you need the requests object, you can fill in the parameters like `requests: Requests` (you need to use the TypeHints format) , You can get the requests object corresponding to the web framework
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

## 3.Exception
### 3.1Exception Handling
Pait will leave the exception to the user to handle it. Under normal circumstances, pait will only throw the exception of `pydantic` and `PaitBaseException`. The user needs to catch the exception and handle it by himself, for example:
```Python
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response

from pait.exceptions import PaitBaseException
from pydantic import ValidationError

async def api_exception(request: Request, exc: Exception) -> Response:
    """
    Handle exception code    
    """

APP = Starlette()
APP.add_exception_handler(PaitBaseException, api_exception)
APP.add_exception_handler(ValidationError, api_exception)
```
### 3.2Error Tip
When you use pait incorrectly, pait will indicate in the exception the file path and line number of the function.
```Bash
  File "/home/so1n/github/pait/pait/func_param_handle.py", line 101, in set_value_to_kwargs_param
    f'File "{inspect.getfile(func_sig.func)}",'
PaitBaseException: 'File "/home/so1n/github/pait/example/starlette_example.py", line 28, in demo_post\n kwargs param:content_type: <class \'str\'> = Header(key=None, default=None) not found value, try use Header(key={key name})'
```
If you need more information, can set the log level to debug to get more detailed information
```Python
DEBUG:root:
async def demo_post(
    ...
    content_type: <class 'str'> = Header(key=None, default=None) <-- error
    ...
):
    pass
```
## 4.How to used in other web framework?
If the web framework is not supported, which you are using.
Can be modified sync web framework according to [pait.web.flask](https://github.com/so1n/pait/blob/master/pait/web/flask.py)
Can be modified async web framework according to [pait.web.starletter](https://github.com/so1n/pait/blob/master/pait/web/starletter.py)
## 5.IDE Support
While pydantic will work well with any IDE out of the box.
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

## 6.Full example
For more complete examples, please refer to[example](https://github.com/so1n/pait/tree/master/example)