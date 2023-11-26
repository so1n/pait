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
