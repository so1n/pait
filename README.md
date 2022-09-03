![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1652600629491%E6%9C%AA%E5%91%BD%E5%90%8D.jpg)
<p align="center">
    <em>Python Modern API Tools, fast to code</em>
</p>

---
**Documentation**: [https://so1n.me/pait/](https://so1n.me/pait/)

**中文文档**: [https://so1n.me/pait-zh-doc/](https://so1n.me/pait-zh-doc/)

---

# pait
Pait is an api tool that can be used in any python web framework (currently only `flask`, `starlette`, `sanic`, `tornado` are supported, other frameworks will be supported once Pait is stable).

> Note:
>
> mypy check 100%
>
> test coverage 95%+ (exclude api_doc)
>
> python version >= 3.7 (support postponed annotations)
>
> The following code does not specify, all default to use the `starlette` framework.

# Feature
 - [x] Parameter checksum automatic conversion (parameter check depends on `Pydantic`)
 - [x] Parameter dependency verification
 - [x] Automatically generate openapi files
 - [x] Swagger, Redoc route
 - [x] gRPC Gateway route
 - [x] TestClient support, support response result verification
 - [x] Support for plugin extensions, such as the Mock plugin

# Installation
```Bash
pip install pait
```
# Simple Example
```python
from typing import Type
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait, add_doc_route
from pait.field import Body
from pait.model.response import PaitResponseModel
from pydantic import BaseModel, Field


class DemoResponseModel(PaitResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel])
async def demo_post(
    uid: int = Body.i(description="user id", gt=10, lt=1000),
    user_name: str = Body.i(description="user name", min_length=2, max_length=4)
) -> JSONResponse:
    return JSONResponse({'uid': uid, 'user_name': user_name})


app = Starlette(routes=[Route('/api', demo_post, methods=['POST'])])
add_doc_route(app)
uvicorn.run(app)
```

# How to used in other web framework?
If the web framework is not supported, which you are using.

Can be modified sync web framework according to [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)

Can be modified async web framework according to [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)
# IDE Support
While pydantic will work well with any IDE out of the box.
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

# Full example
For more complete examples, please refer to [example](https://github.com/so1n/pait/tree/master/example)
