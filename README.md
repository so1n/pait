# pait
Pait is an api tool that can be used in any python web framework (currently only `flask`, `starlette`, `sanic`, `tornado` are supported, other frameworks will be supported once Pait is stable).

Pait allows the Python Web framework to have functions such as parameter type checking, type conversion (depending on Pydantic and inspect), and document output.

> Note:
>
> mypy check 100%
>
> test coverage 95%+ (exclude api_doc)
>
> python version >= 3.7 (support postponed annotations)
>
> The function is being expanded... the documentation may not be perfect
>
> The following code does not specify, all default to use the `starlette` framework.
>
> There is no test case for the document output function, and the function is still being improved

[中文文档](https://github.com/so1n/pait/blob/master/README_ZH.md)
# Feature
 - [x] Parameter checksum automatic conversion (parameter check depends on `Pydantic`)
 - [x] Parameter dependency verification
 - [x] Automatically generate openapi files
 - [x] Support swagger, redoc routing
 - [x] return mock response
 - [x] TestClient support, support response result verification
 - [ ] Support more types of http requests (currently only supports RESTful api)
 - [ ] Combine faker to provide better mock response
 - [ ] Local api document management
# Installation
```Bash
pip install pait
```
# Usage
## 1.type checking and parameter type conversion
### 1.1.Use in route handle
A simple starlette route handler example:
```Python
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def demo_post(request: Request) -> JSONResponse:
    body_dict: dict = await request.json()
    uid: int = body_dict.get('uid', 0)
    user_name: str = body_dict.get('user_name', "")
    # The following code is only for demonstration, in general, we do some wrapping
    if not uid:
        raise ValueError('xxx')
    if type(uid) != int:
        raise TypeError('xxxx')
    if 10 <= uid <= 1000:
        raise ValueError('xxx')

    if not user_name:
        raise ValueError('xxx')
    if type(user_name) != str:
        raise TypeError('xxxx')
    if 2 <= len(user_name) <= 4:
        raise ValueError('xxx')

    return JSONResponse(
        {
            'result': {
                'uid': body_dict['uid'],
                'user_name': body_dict['user_name']
            }
        }
    )


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)


uvicorn.run(app)
```
use pait in starletter route handler:

```Python
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body


@pait()
async def demo_post(
    uid: int = Body.i(description="user id", gt=10, lt=1000),
    user_name: str = Body.i(description="user name", min_length=2, max_length=4)
) -> JSONResponse:
    return JSONResponse({'result': {'uid': uid, 'user_name': user_name}})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)

uvicorn.run(app)
```
It can be seen from the above that the code has been refined a lot. All of this is the role of the `pait` decorator. It finds out how to get the value through the function signature, what is the type of the value, and what is the key corresponding to the value. After assembly, it is handed over to `Pydantic` for verification and conversion, and then returned to the corresponding parameters of the routing function according to the function signature.

for example param: uid
```Python3
from pait.field import Body

uid: int = Body.i(description="user id", gt=10, lt=1000)
```
`pait` will be split into the following parts:

```
<key>: <type> = <request data>
```
The key is the parameter name, type is the parameter type, and request data is the other description of the parameter. For example, body represents the data of the request body, gt is the minimum parameter, and lt is the maximum parameter.



Here is just a simple demo, because we write the model can be reused, so you can save a lot of development time, the above parameters are only used to a way to write, the following will introduce pait support for the two ways to write and use.

### 1.2.Parameter expression supported by pait
pait in order to facilitate the use of users, support a variety of writing methods (mainly the difference between TypeHints)
- TypeHints is PaitBaseModel, mainly used for parameters from multiple `Field`, and want to reuse model:

    PaitBaseModel can be used only for args parameters, it is the most flexible, PaitBaseModel has most of the features of Pydantic. BaseModel, which is not possible with Pydantic.:
    ```Python
    from pait.app.starlette import pait
    from pait.field import Body, Header
    from pait.model.base_model import PaitBaseModel
    ```


    class TestModel(PaitBaseModel):
        uid: int = Body.i()
        content_type: str = Header.i(default='Content-Type')


    @pait()
    async def test(model: PaitBaseModel):
        return {'result': model.dict()}
    ```
- TypeHints is Pydantic.BaseModel, mainly used for parameters are derived from the same `Field`, and want to take the model:

    BaseModel can only be used with kwargs parameters, and the type hints of the parameters must be a class that inherits from `pydantic.BaseModel`, using the example:
    ````Python
    from pydantic import BaseModel

    from pait.app.starlette import pait
    from pait.field import Body


    class TestModel(BaseModel):
        uid: int
        user_name: str


    @pait()
    async def test(model: BaseModel = Body.i()):
        return {'result': model.dict()}
    ````
- When TypeHints is not one of the above two cases:

    can only be used for kwargs parameters and type hints are not the above two cases, if the value is rarely reused, or if you do not want to create a Model, you can consider this approach
    ```Python
    from pait.app.starlette import pait
    from pait.field import Body
    ```


    @pait()
    async def test(uid: int = Body.i(), user_name: str = Body.i()):
        return {'result': {'uid': uid, 'user_name': user_name}}
    ```
### 1.3.Field
Field will help pait know how to get data from request.
Before introducing the function of Field, let’s take a look at the following example. `pait` will obtain the body data of the request according to Field.Body, and obtain the value with the parameter named key. Finally, the parameter is verified and assigned to the uid.

> Note: Use Field.Body() directly, `mypy` will check that the type does not match, then just change to Field.Body.i() to solve the problem.
```Python
from pait.app.starlette import pait
from pait.field import Body


@pait()
async def demo_post(
    # get uid from request body data
    uid: int = Body.i()
) -> None:
    pass
```
`Pait` also supports other functions when performing parameter verification and conversion, all of which are supported by the parameters of `<request data>`:

- default: the function of providing default values, if the request parameter does not have the value of this parameter , The value is used by default

- alias: Since `Content-Type` cannot be named in Python variables, it can only be named with `content_type` according to the naming convention of `Python`, and `content_type` cannot get the value directly from the header, so it can Set alias to `Content-Type`, so that `Pait` can get the value of `Content-Type` in the Header and assign it to the `content_type` variable.

- raw_return: If the value is True, `Pait` will not use the parameter name to get the data, but directly assign the entire data to the corresponding parameter.

```Python
from pait.app.starlette import pait
from pait.field import Body, Header


@pait()
async def demo_post(
    # get uid from request body data
    uid: int = Body.i(default=100),
    # get Content-Type from header
    content_type: str = Header.i(alias='Content-Type'),
    header_dict: str = Header.i(raw_return=True)

):
    pass
```
The above only demonstrates the Body and Header of the field, but there are other fields as well::
- Field.Body   Get the json data of the current request
- Field.Cookie Get the cookie data of the current request
- Field.File   Get the file data of the current request, depending on the web framework will return different file object types
- Field.Form   Get the form data of the current request, if there are multiple duplicate keys, only the first one will be returned
- Field.Header Get the header data of the current request
- Field.Path   Get the path data of the current request (e.g. /api/{version}/test, you can get the version data)
- Field.Query  Get the url parameters of the current request and the corresponding data, if there are multiple duplicate keys, only the first one will be returned
- Field.MultiQuery Get the url parameter data of the current request, and return the list corresponding to the key
- Field.MultiForm Get the form data of the current request, return the list corresponding to the key

All the fields above are inherited from `pydantic.fields.FieldInfo`, most of the parameters here are for api documentation, see for specific usage[pydantic doc](https://pydantic-docs.helpmanual.io/usage/schema/#field-customisation)


In addition there is a field named Depends, he inherits from `object`, he provides the function of dependency injection, he only supports one parameter and the type of function, and the function's parameters are written in the same way as the routing function, the following is an example of the use of Depends, through Depends, you can reuse in each function to get the token function:

```Python
from pait.app.starlette import pait
from pait.field import Body, Depends


def demo_depend(uid: str = Body.i(), password: str = Body.i()) -> str:
    # fake db
    token: str = db.get_token(uid, password)
    return token


@pait()
async def test_depend(token: str = Depends.i(demo_depend)) -> dict:
    return {'token': token}
```

### 1.4.requests object
After using `Pait`, the proportion of the number of times the requests object is used will decrease, so `pait` does not return the requests object. If you need the requests object, you can fill in the parameters like `requests: Requests` (you need to use the TypeHints format) , You can get the requests object corresponding to the web framework
```Python
from starlette.requests import Request

from pait.app.starlette import pait
from pait.field import Body


@pait()
async def demo_post(
        request: Request,
        # get uid from request body data
        uid: int = Body.i()
) -> None:
    pass
```

### 1.5.Exception
#### 1.5.1Exception Handling
Pait will leave the exception to the user to handle it. Under normal circumstances, pait will only throw the exception of `pydantic` and `PaitBaseException`. The user needs to catch the exception and handle it by himself, for example:
```Python
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response

from pait.exceptions import PaitBaseException
from pydantic import ValidationError

async def api_exception(request: Request, exc: Exception) -> None:
    """
    Handle exception code
    """
    if isinstance(exc, PaitBaseException):
        pass
    elif isinstance(exc, ValidationError):
        pass
    else:
        pass

APP = Starlette()
APP.add_exception_handler(PaitBaseException, api_exception)
APP.add_exception_handler(ValidationError, api_exception)
```
#### 1.5.2Error Tip
When you use `pait` incorrectly, `pait` will indicate in the exception the file path and line number of the function.
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
## 2.Document Generation

`pait` will automatically capture the request parameters and url, method and other information of the routing function.
In addition, it also supports labeling some relevant information. These labels will only be loaded into the memory when the Python program starts running, and will not affect the performance of the request, as in the following example:

```Python
from pait.app.starlette import pait
from pait.model.status import PaitStatus

from example.param_verify.model import UserSuccessRespModel, FailRespModel


@pait(
  author=("so1n",),
  group="user",
  status=PaitStatus.release,
  tag=("user", "post"),
  response_model_list=[UserSuccessRespModel, FailRespModel],
)
def demo() -> None:
  pass
```
Param:
- author: List of authors who wrote the interface
- group: The group to which the interface belongs (This option is currently not used for openapi)
- status: The status of the interface, currently only supports several states of `PaitStatus` (This option will only be used for openapi and marked as deprecated if it is offline)
  - default status:
    - undefined: undefined
  - in development:
    - design: Interface design
    - dev: Under development and testing
  - Development completed:
    - integration: integration test
    - complete: development completed
    - test: testing
  - online:
    - release: online
  - offline:
    - abnormal: The interface is abnormal and needs to be offline
    - maintenance: In maintenance
    - archive: archive
    - abandoned: abandoned
- tag: interface tag
- response_model_list: return data, Need to inherit from `pait.model.PaitResponseModel`, Since `pait` is an extension of the web framework and will not modify the code of the framework, this parameter will not be used for ordinary request judgment (nor should it be used in the production environment). It is currently only used for document generation, mock response generation and TestClient verification.

### 2.1.openapi
#### 2.1.1openapi doc output
Currently pait supports most of the functions of openapi, a few unrealized features will be gradually improved through iterations (response-related more complex)

The openapi module of pait supports the following parameters (more parameters will be provided in the next version):
- title: openapi's title
- open_api_info: openapi's info param
- open_api_tag_list: related description of openapi tag
- open_api_server_list: openapi server list
- type_: The type of output, optionally json and yaml
- filename: Output file name, or if empty, output to terminal

The following is the sample code output from the openapi documentation (modified by the 1.1 code). See [Example code](https://github.com/so1n/pait/tree/master/example/api_doc) and [doc example](https://github.com/so1n/pait/blob/master/example/api_doc/example_doc)
```Python
import uvicorn

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

from pait.field import Body
from pait.app.starlette import pait
from pydantic import (
    BaseModel,
    conint,
    constr,
)


# Create a Model based on Pydantic.BaseModel
class PydanticModel(BaseModel):
    uid: conint(gt=10, lt=1000)  # Whether the auto-check type is int, and whether it is greater than or equal to 10 and less than or equal to 1000
    user_name: constr(min_length=2, max_length=4)  # Whether the auto-check type is str, and whether the length is greater than or equal to 2, less than or equal to 4



# Decorating functions with the pait decorator
@pait()
async def demo_post(
    # pait through the Body () to know the current need to get the value of the body from the request, and assign the value to the model,
    # and the structure of the model is the above PydanticModel, he will be based on our definition of the field automatically get the value and conversion and judgment
    model: PydanticModel = Body.i()
):
    # Get the corresponding value to return
    return JSONResponse({'result': model.dict()})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)

uvicorn.run(app)
# --------------------

from pait.app.starlette import load_app
from pait.api_doc.open_api import PaitOpenApi


# Extracting routing information to pait's data module
pait_dict = load_app(app)
# Generate openapi for routing based on data from the data module
PaitOpenApi(pait_dict)
```
#### 2.1.2.OpenApi Route
`Pait` currently supports openapi.json routing, and also supports page display of `Redoc` and `Swagger`, and these only need to call the `add_doc_route` function to add three routes to the `app` instance:
- /openapi.json
- /redoc
- /swagger
If you want to define a prefix, such as /doc/openapi.json, just pass in /doc through the prefix parameter. Specific examples are as follows:
```Python
import uvicorn  # type: ignore
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body


# Create a Model based on Pydantic.BaseModel
class UserModel(BaseModel):
    # Whether the auto-check type is int, and whether it is greater than or equal to 10 and less than or equal to 1000
    uid: int = Field(description="user id", gt=10, lt=1000)
    # Whether the auto-check type is str, and whether the length is greater than or equal to 2, less than or equal to 4
    user_name: str = Field(description="user name", min_length=2, max_length=4)


# Decorating functions with the pait decorator
@pait()
async def demo_post(
    # pait through the Body () to know the current need to get the value of the body from the request, and assign the value to the model,
    # and the structure of the model is the above PydanticModel, he will be based on our definition of the field automatically get the value and conversion and judgment
    model: UserModel = Body.i()
) -> JSONResponse:
    # Get the corresponding value to return
    return JSONResponse({'result': model.dict()})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)
# Inject the route into the app
add_doc_route(app)
# Inject the route into the app, and prefix it with /doc
add_doc_route(app, prefix='/doc')
```
### 2.2.Other doc output
> Note: The function is being improved...

In addition to parameter verification and conversion, pait also provides the ability to output api documentation, which can be configured with simple parameters to output perfect documentation.

Note: Currently only md documents and openapi documents for json and yaml are supported for output.For the output of md, see
[doc example](https://github.com/so1n/pait/blob/master/example/api_doc/example_doc)


## 3.Implicit and explicit introduction
`pait` provides support for multiple frameworks. If only one of the frameworks is installed in a project, then you can use implicit import:
```Python3
from pait.app import add_doc_route, load_app, pait

```
However, if multiple frameworks are installed at the same time, the above introduction will throw an error. It is recommended to use explicit introduction, such as:
```Python3
from pait.app.starlette import add_doc_route, load_app, pait

```
## 4.config, data and load_app
- data

  Since `pait` provides functional support through a decorator, all data is injected into meta data when the compiler is started, providing support for subsequent document generation and other functions.
- load_app

  There are a lot of routing function information in meta data, but it lacks key parameters such as `url`, `method`, etc.
So you also need to use load_app to bind the relevant parameters to the routing function data decorated by the `pait` decorator in the meta data. The method of use is very simple, but remember that you must register all routes before calling:
```Python3
  from starlette.applications import Starlette

  from pait.app.starlette import load_app

  app: Starlette = Starlette()
  # error
  load_app(app)
  # --------
  # app.add_route
  # --------

  # success
  load_app(app)
  ```
- config
config can provide some configuration support for `pait`, it needs to be initialized as soon as possible. The best initialization position is to initialize before app initialization, and only one initialization is allowed during the entire runtime.
  ```Python
  from starlette.applications import Starlette

  from pait.app.starlette import load_app
  from pait.g import config

  config.init_config(author="so1n")
  app: Starlette = Starlette()
  # --------
  # app.add_route
  # --------
  load_app(app)
  ```

Parameter introduction:
- author: The global default API author, if the author parameter in `@pait` is empty, it will call `config.author` by default.
- status: The global default API status, if the status in `@pait` is empty, it will be called by default to `config.status`
- enable_mock_response: Decide whether this run will return a normal response or a mock response based on `response_model`
- enable_mock_response_filter_fn: Multiple `response_model` are supported by default, and the mock response only takes the first `response_model` by default. If you feel that this does not meet the `response_model` you want, you can configure this function to return the results you want
- block_http_method_set: Some web frameworks will automatically help add some routing functions to request methods such as `HEAD`. `pait` cannot recognize which are added by the framework and which are added by the user. Users can block some `methods` through this parameter
- default_response_model_list: When designing some API interfaces, there are usually some default exception responses, and repeated configuration is very troublesome. can apply to the global by configuring this parameter
- json_type_default_value_dict: Configure the default value of the json type
## 5.TestClientHelper
`pait` encapsulates a corresponding `TestCLientHelper` class for each framework, through which test cases can be written more conveniently, and the result data structure can be compared with `response_model` for verification. [starlette example](https://github.com/so1n/pait/blob/master/tests/test_app/test_starlette.py#L80)

Parameter Description:
  - client: The test client corresponding to the framework
  - func: Corresponding to the routing function decorated by `pait`
  - pait_dict: `pait` meta data, if it is empty, it will be automatically generated internally
  - body_dict: Requested json data
  - cookie_dict: Requested cookie data
  - file_dict: Requested file data
  - form_dict: Requested form data
  - header_dict: Requested header data
  - path_dict: Requested path data
  - query_dict: Requested query data


Description of response_model generation results:
If response_model has a `default` value, it will be directly referenced to the `default` value, otherwise the default value of the value type is used (configurable through config)
## 6.How to used in other web framework?
If the web framework is not supported, which you are using.
Can be modified sync web framework according to [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)

Can be modified async web framework according to [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)
## 7.IDE Support
While pydantic will work well with any IDE out of the box.
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

## 8.Full example
For more complete examples, please refer to [example](https://github.com/so1n/pait/tree/master/example)
