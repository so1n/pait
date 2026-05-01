In the process of using `Pait`,
may find that multiple route functions use the same parameter configuration, as shown in the following code:
```Python
from pait.app.any import pait
from pait.model.status import PaitStatus

@pait(status=PaitStatus.test)
def demo1() -> None:
    pass


@pait(status=PaitStatus.test)
def demo2() -> None:
    pass

@pait(status=PaitStatus.test)
def demo3() -> None:
    pass
```
There are 3 route functions in the sample code, and since they are still in the testing phase,
the value of their `status` is `PaitStatus.test`.
After a period of testing, the code has become complete and ready to be released,
the status of the route functions needs to be changed to `Relese`,
so each route function has to be manually changed to `PaitStatus.test`.
When there are a lot of route functions, manually switching the `status` of each of them can be very cumbersome.
For this reason, it is possible to define a common `Pait` and use it for all route functions,
so that these route functions can share the same `Pait` and thus the same configuration functionality.


!!! note
    - 1.The examples provided in this section are based on the `Starlette` framework, while other frameworks differ only in the `import` statement for importing the `Pait` class.
    - 2.This section focuses on the usage of the `Pait` class. The role of different properties is described in the corresponding documentation.
    - 3.`Pait` can be thought of as a container for hosted data; as long as their properties are consistent, then their functionality is the same, even if there is no relationship between them.

## 1.Custom Pait
In the previous introduction to `Pait`, `Pait` is imported through the following syntax:
```Python
from pait.app.flask import pait
from pait.app.sanic import pait
from pait.app.starlette import pait
from pait.app.tornado import pait
```

Imported `pait` is a single instance of each Web framework corresponding to the `Pait` class,
in the customization of `Pait`, it is recommended to start through the Web framework corresponding to the `Pait` class,
such as the following sample code:
```py hl_lines="6 8 13 18"
from pait.app.starlette import Pait
from pait.model.status import PaitStatus
from starlette.responses import Response


global_pait: Pait = Pait(status=PaitStatus.test)

@global_pait()
async def demo() -> Response:
    pass


@global_pait()
async def demo1() -> Response:
    pass


@global_pait()
async def demo2() -> Response:
    pass
```
The sample code of the first highlighting code is based on `Pait` class to create a `Pait` instance called `global_pait`,
it is similar to the framework corresponding `pait` instance,
the only difference is that its `status` attribute is specified as `PaitStatus.test`.
The other highlighted code applies `global_pait` to all route functions, and the `status` of the route function is the same as the `status` of the code below:
```Python
@pait(status=PaitStatus.test)
async def demo() -> Response:
    pass
```

## 2.Create child Pait
A `Pait` can create its own child `Pait` through the `create_sub_pait` method,
and each child `Pait`'s attributes are cloned from the parent `Pait`, as in the following code:
```Python
from pait.app.starlette import Pait
from pait.model.status import PaitStatus

global_pait: Pait = Pait(status=PaitStatus.test)
other_pait: Pait = global_pait.create_sub_pait()
```
In the sample code, `other_pait` is created by `global_pait`, so its `status` attribute is the same as `global_pait`.

If you don't want to clone the attributes of the parent `Pait`,
then you can override the attributes of the parent `Pait` by specifying the attributes of the child `Pait` when creating the child `Pait`,
as in the following code:
```Python
from pait.app.starlette import Pait

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")
```

The `author` attribute of both `global_pait` and `user_pait` is `("so1n", )`.
However, since the value of `group` was specified as `user` when `user_pait` was created,
the `group` attributes of `global_pait` and `user_pait` are different, they are `global` and `user`.

## 3.Use of Pait
The usage of the sub `Pait` is identical to that of the standard `pait` decorator,
the only difference being that it already carries some of the configuration data on its own,
and after decorating the route function,
it will cause the route function to have the corresponding configuration functionality.
The following code:
```Python
from pait.app.starlette import Pait
from starlette.responses import JSONResponse

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@user_pait()  # group="user"
async def user_login() -> JSONResponse:
    pass

@user_pait()  # group="user"
async def user_logout() -> JSONResponse:
    pass

@global_pait()  # group="global"
async def get_server_timestamp() -> JSONResponse:
    pass
```
The route functions `user_login` and `user_logout` are both decorated by `user_pait`, so the value of their `group` is `user`;
And the route function `get_server_timestamp` is decorated by `global_pait`, so the value of `group` is `global`.


In addition,
it is possible to overwrite the original attribute values of the child `pait` when the child `pait` decorates the route function.
As in the following code, the `group` attribute of `user_logout` of the route function in the highlighted code changes to `user-logout` and no longer to `user`:
```py hl_lines="12"
from pait.app.starlette import Pait
from starlette.responses import JSONResponse

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@user_pait()
async def user_login() -> JSONResponse:
    pass

@user_pait(group="user-logout")
async def user_logout() -> JSONResponse:
    pass

@global_pait()
async def get_server_timestamp() -> JSONResponse:
    pass
```

In addition to overwriting the original value, some attributes also support appending values, as shown in the following code:
```py hl_lines="13"
from pait.app.starlette import Pait
from starlette.responses import JSONResponse

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@user_pait()  # group="user"
async def user_login() -> JSONResponse:
    pass


@user_pait(append_author=("Other Author",))  # group="user"; author=("so1n", "Other Author",)
async def user_logout() -> JSONResponse:
    pass


@global_pait()  # group="global"
async def get_server_timestamp() -> JSONResponse:
    pass
```
The highlighted portion of the code uses the `append_xxx` family of `Pait` parameters to append the value so that the `author` value of `user_logout` becomes `("so1n", "Other Author")`.

!!! note
    The appended value will only be added to the end of the sequence,
    while some functions such as `Pre-Depend` need to consider the order in which the values are placed,
    so please pay attention to whether the appending order is appropriate or not when use it.

## 4.Common Pait parameters

`Pait` has many optional parameters. Some of them only affect OpenAPI data, while others affect runtime behavior.
The commonly used parameters are listed below:

| Parameter | Description |
|-----------|-------------|
| default_field_class | Default `Field` class used when a route parameter does not explicitly set a `Field` |
| pre_depend_list | Dependency functions executed before the route function |
| operation_id | Explicit OpenAPI operation id |
| author | Route author metadata |
| desc | Route description, used by OpenAPI |
| summary | Route summary, used by OpenAPI |
| name | Route name, used as part of OpenAPI operation id generation |
| status | Route status, also used to infer OpenAPI deprecated state |
| group | Route group metadata |
| tag | Route tag list, each item should be a `pait.model.tag.Tag` object |
| extra_openapi_model_list | Extra request models that cannot be inferred from route parameters |
| response_model_list | Response model list; Pydantic `BaseModel` can be used directly for JSON responses |
| plugin_list | Plugins executed before the route function |
| post_plugin_list | Plugins executed after the route function |
| sync_to_thread | Run sync route/dependency code in the thread pool when used by async frameworks |
| feature_code | Extra code used to generate a unique `pait_id` for dynamically generated routes |
| auto_build | Whether to build the plugin stack immediately when the route core model is generated |
| tip_exception_class | Custom tip exception class; set to `None` to disable tip wrapping |
| extra | Extra data reserved for plugins |

### 4.1.Extra OpenAPI models

Normally `Pait` can infer request OpenAPI data from route parameters. Some request styles cannot be described by a normal
parameter, for example streaming upload data that is read from the request body. In these cases, use
`extra_openapi_model_list` to supplement the OpenAPI request model.

When creating a child `Pait`, use `append_extra_openapi_model_list` if the child should keep the parent's extra OpenAPI
models and append new ones.

### 4.2.Sync to thread

For async frameworks, `sync_to_thread=True` lets `Pait` run sync route functions and sync dependency functions in a thread
pool. This is useful when an async application needs to call blocking code such as sync database clients or file processing
logic.

```python
from pait.app.starlette import pait
from pait.field import Json
from starlette.responses import JSONResponse


def sync_heavy_task(data: str) -> str:
    return f"Processed: {data}"


@pait(sync_to_thread=True)
def sync_route(data: str = Json.i()) -> JSONResponse:
    result = sync_heavy_task(data)
    return JSONResponse({"result": result})
```

`sync_to_thread` only changes how the route/dependency call is scheduled. It does not make blocking code faster; it avoids
blocking the event loop while the blocking code is running.

### 4.3.Tip exception class

`TipException` wrapping is enabled by default. It can be configured per route:

```python
from pait.app.starlette import pait


@pait(tip_exception_class=None)
async def demo() -> None:
    pass
```

It can also be configured globally:

```python
from pait.g import config


config.init_config(tip_exception_class=None)
```

Setting `tip_exception_class` on a custom `ParamHandler` is still compatible, but it is deprecated and should be replaced
by `@pait(tip_exception_class=...)` or `config.init_config(tip_exception_class=...)`.

## 5.CBV preload

`Pait.pre_load_cbv` can preload a class-based view and apply shared `Pait` parameters to its HTTP methods before the route
is registered. It is mainly used by framework adapters and `APIRoute.add_cbv_route`.

```python
from pait.app.flask import Pait
from pait.model.tag import Tag


class UserView:
    def get(self) -> dict:
        return {"method": "get"}


api_pait = Pait(tag=(Tag("user"),), group="user")
api_pait.pre_load_cbv(UserView, desc="User API")
```

When `load_app(app, auto_cbv_handle=True)` is used, `Pait` will also try to handle class-based routes automatically while
loading application route metadata. This is enabled by default for supported frameworks.

Some route-only parameters cannot be used by `pre_load_cbv`, including `sync_to_thread`, `feature_code`, `plugin_list`,
`post_plugin_list`, `param_handler_plugin`, `name` and `operation_id`.
