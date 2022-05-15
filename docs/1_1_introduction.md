# Introduction
Using `Pait` for parameter type conversion and parameter verification is very simple, for example:
``` py hl_lines="11 13 14"  linenums="1"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body


# Decorate function with the pait decorator
@pait()
async def demo_post(
    uid: int = Body.i(description="user id", gt=10, lt=1000),
    user_name: str = Body.i(description="user name", min_length=2, max_length=4)
) -> JSONResponse:
    # get value and return
    return JSONResponse({'result': {'uid': uid, 'user_name': user_name}})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)

uvicorn.run(app)
```
Line 11 of the above code is the running core of `Pait`,
and all the running functions of `Pait` are implemented in this decorator。

Line 11 of the above code is the running core of `Pait`.
All running functions of `Pait` are implemented in this decorator.
In this core, the function signature corresponding to the function will be obtained through `inspect` ,
and generate a `pydantic.BaseModel` object through the function signature,
and then use the object checksum to convert the requested value and return it to the corresponding parameters of the function according to the function signature.

The 13 and 14 lines of code are the parameters filled in by the developer.
When the developer writes the function,
only needs to write the parameters of the function as key parameters in the format similar to `<name>:<type>=<default>`.
in addition to conforming to the key parameter standard of `Python`, `Pait` will also give other meanings:

- `name` The parameter name, in most cases, will be used as the Key to request the resource to obtain the corresponding value.
- `type` The type corresponding to the value, which `Pait` will use for parameter verification and conversion.
- `default` The `field` object of `Pait`, different `field` represent getting values from different request types, and the properties of the object tell `Pait` how to preprocess the value obtained from the request.

Taking the `uid` parameter above as an example, `Pait` will obtain the Json data from the request through the Body, and then use the Key as the uid to obtain the corresponding value from the Json data and convert or verify whether it is an `int` type, and finally Then judge whether the value is between 10-1000, if not, report an error directly, if so, assign it to the variable `uid`.

!!! note
    When using Body() directly, mypy will check the type mismatch, and Body.i() is compatible with this problem. In general, it is recommended to use Body.i() directly.
