`field` plays a crucial role in `Pait`. In addition to using `field` to obtain data sources, `Pait` also uses it to achieve many other functions. In this chapter, only parameter validation is emphasized. this piece.

## 1.Kind of Field

In addition to the Body mentioned above, `Field` also has other types, their names and functions are as follows:

- Body: Get the json data of the current request
- Cookie: Get the cookie data of the current request (note that the current cookie data will be converted into a Python dictionary, which means that the key of the cookie cannot be repeated. At the same time, when the Field is a cookie, the type is preferably str)
- File：Get the file object of the current request, which is consistent with the file object of the web framework
- Form：Get the form data of the current request. If there are multiple duplicate Keys, only the first value will be returned
- Header: Get the header data of the current request
- Path: Get the path data of the current request, such as `/api/{version}/test`, will get the version data
- Query: Get the data corresponding to the Url parameter of the current request. If there are multiple duplicate keys, only the first value will be returned
- MultiForm：Get the form data of the current request, and return the data list corresponding to the Key
- MultiQuery：Get the data corresponding to the Url parameter of the current request, and return the data list corresponding to the Key

The specific usage of each type is very simple, just fill in the `default` position in `<name>:<type>=<default>`, take this code as an example (in order to ensure that it can be copied and pasted and run, no demo field.File):
```Python
from typing import List, Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field

@pait()
async def demo(
    form_a: str = field.Form.i(),
    form_b: str = field.Form.i(),
    multi_form_c: List[str] = field.MultiForm.i(),
    cookie: dict = field.Cookie.i(raw_return=True),
    multi_user_name: List[str] = field.MultiQuery.i(min_length=2, max_length=4),
    age: int = field.Path.i(gt=1, lt=100),
    uid: int = field.Query.i(gt=10, lt=1000),
    user_name: str = field.Query.i(min_length=2, max_length=4),
    email: Optional[str] = field.Query.i(default="example@xxx.com"),
    accept: str = field.Header.i()
) -> JSONResponse:
    """Test the use of all BaseRequestResourceField-based"""
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "accept": accept,
                "form_a": form_a,
                "form_b": form_b,
                "form_c": multi_form_c,
                "cookie": cookie,
                "multi_user_name": multi_user_name,
                "age": age,
                "uid": uid,
                "user_name": user_name,
                "email": email,
            },
        }
    )

app = Starlette(
    routes=[
        Route("/api/demo/{age}", demo, methods=["POST"]),
    ]
)


uvicorn.run(app)
```
This code comes from[pait base field example](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py#L163),
And made some small changes, the main responsibility of this interface is to return the parameters to the caller in json format.

Next, use the `curl` command to perform a request test. Through the output results, it can be found that `Pait` can accurately get the corresponding value through the type of `field`, and assign it to the variable。
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/demo/12?uid=99&user_name=so1n&multi_user_name=so1n' \
  -H 'accept: application/json' \
  -H 'Cookie: cookie=cookie=test cookie' \
  -H 'Content-Type: multipart/form-data' \
  -F 'form_a=a' \
  -F 'form_b=b' \
  -F 'multi_form_c=string,string'

{
    "code": 0,
    "msg": "",
    "data": {
        "accept": "application/json",
        "form_a": "a",
        "form_b": "b",
        "form_c": [
            "string,string"
        ],
        "cookie": {
            "cookie": "cookie=test cookie"
        },
        "multi_user_name": [
            "so1n"
        ],
        "age": 12,
        "uid": 99,
        "user_name": "so1n",
        "email": "example@xxx.com"
    }
}
```
## 2.Field feature
As can be seen from the above example, the `email` parameter is not included in the request, but the value of `email` in the response value returned by the interface is `example@xxx.com`，
This is because when I fill in the `field` of `email`, I fill in `example@xxx.com` into the default value, so that `Pait` can not get the corresponding value of the variable, but also can The default value is assigned to the corresponding variable。

In addition to default values, `field` also has many feature, most of which are derived from `pydantic.Field`, which `field` inherits.


### 2.1.default
`Pait` supports default value through this parameter. If there is no default value, you can simply leave the value of this parameter blank.

The sample code is as follows, both interfaces directly return the obtained value `demo_value`, where the `demo` interface has a default value, the default value is string 123, and the `demo1` interface has no default value:
```py hl_lines="20 25"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field
from pait.exceptions import TipException


async def api_exception(request: Request, exc: Exception) -> PlainTextResponse:
    """Extract exception information and return it as a response"""
    if isinstance(exc, TipException):
        exc = exc.exc
    return PlainTextResponse(str(exc))


@pait()
async def demo(demo_value: str = field.Query.i(default="123")) -> PlainTextResponse:
    return PlainTextResponse(demo_value)


@pait()
async def demo1(demo_value: str = field.Query.i()) -> PlainTextResponse:
    return PlainTextResponse(demo_value)


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
        Route("/api/demo1", demo1, methods=["GET"]),
    ]
)

app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
```
Using `curl` call, can find that for the interface `/api/demo` with a default value, when no parameter demo_value is passed, the default return value is 123, and when the parameter 456 is passed, the return value is 456:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo"
123
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=456"
456
```
And the request without parameters will see an error, indicating that the value of `demo_value` is not found:
```bash
➜  curl "http://127.0.0.1:8000/api/demo1"
Can not found demo_value value
```

### 2.2.default_factory
This parameter is used when the default value is a function, and can be used to fill in a default value similar to `datetime.datetime.now` that is generated after receiving a request.

The sample code is as follows. The default value of the first interface is the current time, and the default value of the second interface is uuid. The return value of each call is generated when the request is received.:
```py hl_lines="14 21"
import datetime
import uuid
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(
    now: datetime.datetime = field.Query.i(default_factory=datetime.datetime.now)
) -> PlainTextResponse:
    return PlainTextResponse(now)


@pait()
async def demo1(
    demo_value: str = field.Query.i(default_factory=lambda: uuid.uuid4().hex)
) -> PlainTextResponse:
    return PlainTextResponse(demo_value)


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
        Route("/api/demo1", demo1, methods=["GET"]),
    ]
)

uvicorn.run(app)
```
Using `curl` calls can find that the results returned each time are different:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo"
2022-02-07T14:54:29.127519
➜  ~ curl "http://127.0.0.1:8000/api/demo"
2022-02-07T14:54:33.789994
➜  ~ curl "http://127.0.0.1:8000/api/demo1"
7e4659e18103471da9db91ed4843d962
➜  ~ curl "http://127.0.0.1:8000/api/demo1"
ef84f04fa9fc4ea9a8b44449c76146b8
```
### 2.3.alias
Aliases for parameters, some parameters may be named `Content-Type`, but Python does not support this naming method, you can use aliases in this case。

The sample code is as follows:
```py hl_lines="12"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(
    content_type: str = field.Header.i(alias="Content-Type")
) -> PlainTextResponse:
    return PlainTextResponse(content_type)


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])

uvicorn.run(app)
```
Using the `curl` call, it can be found that `Pait` normally extracts the `Content-Type` value from the Header and assigns it to the content type:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" -H "Content-Type:123"
123
```

### 2.4.gt, ge, lt, le, multiple of digital check
These values are all check digits for legality and are only used for numeric types, but their functions are different：

- gt：For numeric types only, it will check if the numeric value is greater than this value, and also add the `exclusiveMinimum` property in the Open API.
- ge：Only used for numeric types, it will check whether the value is greater than or equal to this value, and also add the `exclusiveMinimum` attribute in the Open API。
- lt：Only used for numeric types, it will check whether the value is less than this value, and also add the `exclusiveMaximum` attribute in the Open API。
- le：Only used for numeric types, it will check whether the value is less than or equal to this value, and also add the `exclusiveMaximum` attribute in the Open API。
- multiple_of：For numbers only, checks if the number is a multiple of the specified value.

The sample code is as follows, this sample code has only one interface, but accepts three parameters `demo_value1`, `demo_value2`, `demo_value3`, they only accept three numbers that are greater than 1 and less than 10; equal to 1 and a multiple of 3:
```py hl_lines="23-25"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field
from pait.exceptions import TipException
from pydantic import ValidationError


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """Extract exception information and return it as a response"""
    if isinstance(exc, ValidationError):
        # parsingPydanticSErrorThrow
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(
    demo_value1: int = field.Query.i(gt=1, lt=10),
    demo_value2: int = field.Query.i(ge=1, le=1),
    demo_value3: int = field.Query.i(multiple_of=3),
) -> JSONResponse:
    return JSONResponse({"data": [demo_value1, demo_value2, demo_value3]})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)

uvicorn.run(app)
```
Using the `curl` call, you can find that the first request meets the requirements and gets the desired response result. The second request has all three parameters wrong, and returns the error message of `Pydantic.ValidationError`. From the error message, you can It is simple to see that the three parameters do not meet the qualifications of the interface settings：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=2&demo_value2=1&demo_value3=3"
{"data":[2,1,3]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=11&demo_value2=2&demo_value3=2"
{
    "data": [
        {
            "loc": [
                "demo_value1"
            ],
            "msg": "ensure this value is less than 10",
            "type": "value_error.number.not_lt",
            "ctx": {
                "limit_value": 10
            }
        },
        {
            "loc": [
                "demo_value2"
            ],
            "msg": "ensure this value is less than or equal to 1",
            "type": "value_error.number.not_le",
            "ctx": {
                "limit_value": 1
            }
        },
        {
            "loc": [
                "demo_value3"
            ],
            "msg": "ensure this value is a multiple of 3",
            "type": "value_error.number.not_multiple",
            "ctx": {
                "multiple_of": 3
            }
        }
    ]
}
```
### 2.5. array check(min_items，max_items)
These values are used to check whether the array is legal or not. They are only used for the type of the array. Their feature are different.：

- min_items：For array types only, it will check whether the word list is greater than or equal to the specified value.
- max_items： Only for array types, it will check whether the word list is less than or equal to the specified value。

The sample code is as follows, the interface obtains the array of parameter `demo value` from the request Url through `field.MultiQuery`, and returns it to the calling end, where the length of the array is limited to greater than or equal to 1 and less than or equal to 2：
```py hl_lines="25"
from typing import List
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field
from pait.exceptions import TipException
from pydantic import ValidationError


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """Extract exception information and return it as a response"""
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(
    demo_value: List[int] = field.MultiQuery.i(min_items=1, max_items=2)
) -> JSONResponse:
    return JSONResponse({"data": demo_value})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)

uvicorn.run(app)
```
As in 2.4, through the `curl` call, it can be found that the legal parameters will be released, and the illegal parameters will throw an error：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1"
{"data":[1]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1&demo_value=2"
{"data":[1,2]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1&demo_value=2&demo_value=3"
{
    "data": [
        {
            "loc": [
                "demo_value"
            ],
            "msg": "ensure this value has at most 2 items",
            "type": "value_error.list.max_items",
            "ctx": {
                "limit_value": 2
            }
        }
    ]
}
```
### 2.6.String check(min_length，max_length，regex)
These values are used to check whether the string is legal or not. They are only used for the type of string, and their feature are different:

- min_length：Only used for string type, it will check whether the length of the string is greater than or equal to the specified value。
- max_length：For string type only, it will check whether the length of the string is less than or equal to the specified value.
- regex：For string type only, it will check whether the string matches the regular expression.

The sample code is as follows, the interface needs to get a value from Url, the length of this value is 6, and it must start with the English letter u:
```py hl_lines="24"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field
from pait.exceptions import TipException
from pydantic import ValidationError


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """Extract exception information and return it as a response"""
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(
    demo_value: str = field.Query.i(min_length=6, max_length=6, regex="^u")
) -> JSONResponse:
    return JSONResponse({"data": demo_value})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)

uvicorn.run(app)
```
Use `curl` to make three requests, the first is normal data, the second is not conforming to the regular expression, and the third is that the length does not conform：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=u66666"
{"data":"u66666"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=666666"
{"data":[{"loc":["demo_value"],"msg":"string does not match regex \"^u\"","type":"value_error.str.regex","ctx":{"pattern":"^u"}}]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1"
{"data":[{"loc":["demo_value"],"msg":"ensure this value has at least 6 characters","type":"value_error.any_str.min_length","ctx":{"limit_value":6}}]}
```
### 2.7.raw_return
The default value of this parameter is `False`. If it is `True`, `Pait` will not obtain the value from the request data according to the parameter name or `alias` as the key, but will return the entire request value to the corresponding variable。

The sample code is as follows, the interface is a POST interface, it requires two values, the first value is the Json parameter passed by the entire client, and the second value is the value of Key in the Json parameter passed by the client:

```py hl_lines="12-13"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(
    demo_value1: dict = field.Body.i(raw_return=True),
    a: str = field.Body.i(),
) -> JSONResponse:
    return JSONResponse({
        "demo_value": demo_value1,
        "a": a
    })


app = Starlette(routes=[Route("/api/demo", demo, methods=["POST"])])

uvicorn.run(app)
```
Called with `curl`, you can see that the result is as expected:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" -X POST -d '{"a": "1", "b": "2"}' --header "Content-Type: application/json"
{"demo_value":{"a":"1","b":"2"},"a":"1"}
```

### 2.8.Other Feature
In addition to the above functions, `Pait` has other properties, but they are only related to OpenAPI, so this chapter only briefly introduces:

- link：The link feature used to support Open Api.
- media_type：The media_type corresponding to Field is used for the parameter media type classification of OpenAPI Scheme.
- example：Example values for documentation, and Mock features like Mock Request and Response, supporting both variables and callables, for example `datetime.datetim.now`. Recommended for use with [faker](https://github.com/joke2k/faker).
- openapi_serialization：The serialization method used for this value in the Open API Schema。
- description: Parameter description for Open API
