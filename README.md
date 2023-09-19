![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1652600629491%E6%9C%AA%E5%91%BD%E5%90%8D.jpg)
<p align="center">
    Pait(π tool) - <em>Python Modern API Tools, easier to use web frameworks/write API routing</em>
</p>
<p align="center">
    <a href="https://codecov.io/gh/so1n/pait" target="_blank">
        <img src="https://codecov.io/gh/so1n/pait/branch/master/graph/badge.svg?token=NEVM1VODHR" alt="Coverage">
    </a>
</p>
<p align="center">
    <a href="https://pypi.org/project/pait/" target="_blank">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/pait">
    </a>
    <a href="https://pypi.org/project/pait/" target="_blank">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/pait">
    </a>
</p>
<p align="center">
    <a href="https://github.com/so1n/pait/actions?query=event%3Apush+branch%3Amaster" target="_blank">
        <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/so1n/pait/python-package.yml">
    </a>
    <a href="https://github.com/so1n/pait/releases" target="_blank">
        <img alt="GitHub release (release name instead of tag name)" src="https://img.shields.io/github/v/release/so1n/pait?include_prereleases">
    </a>
    <a href="https://github.com/so1n/pait/actions?query=event%3Apush+branch%3Amaster" target="_blank">
        <img src="https://github.com/so1n/pait/actions/workflows/python-package.yml/badge.svg?event=push&branch=master" alt="Test">
    </a>
</p>
<p align="center">
    <a href="https://github.com/so1n/pait/tree/master/example" target="_blank">
        <img src="https://img.shields.io/badge/Support%20framework-Flask%2CSanic%2CStarlette%2CTornado-brightgreen" alt="Support framework">
    </a>
</p>


---
**Documentation**: [https://so1n.me/pait/](https://so1n.me/pait/)

**中文文档**: [https://so1n.me/pait-zh-doc/](https://so1n.me/pait-zh-doc/)

---

# Warning
There are changes between the current version and the 0.8 version of the API, For more information, please refer to [1.0.0version change](https://github.com/so1n/pait/blob/master/CHANGELOG.md)

# pait

Pait is an api tool that can be used in any python web framework, the features provided are as follows:
 - [x] Parameter checksum automatic conversion (parameter check depends on `Pydantic`)
 - [x] Parameter dependency verification
 - [x] Automatically generate openapi files
 - [x] Swagger, Redoc, Rapidoc, Elements, OpenAPI route
 - [x] gRPC Gateway route(After version 1.0, this feature has been migrated to [grpc-gateway](https://github.com/python-pai/grpc-gateway))
 - [x] TestClient support, support response result verification
 - [x] Support for plugin extensions, such as the Mock plugin, CheckResponse Plugin, Cache Response Plugin
 - [X] Support Pydantic V1 and V2
 - [ ] WebSocket support
 - [ ] SSE support
 - [ ] Auto API Test support


> Note:
>
> - mypy check 100%
>
> - python version >= 3.7 (support postponed annotations)



# Installation
```Bash
pip install pait --pre
```

# Simple Example
```python
from typing import Type
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body
from pait.openapi.doc_route import add_doc_route
from pait.model.response import JsonResponseModel
from pydantic import BaseModel, Field


class DemoResponseModel(JsonResponseModel):
    """demo post api response model"""
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
See [documentation](https://so1n.me/pait/) for more features

# Support Web framework

| Framework | Description            |
|-----------|------------------------|
| Flask     | All features supported |
| Sanic     | All features supported |
| Starlette | All features supported |
| Tornado   | All features supported |
| Django    | Coming soon            |


If the web framework is not supported(which you are using).

Can be modified sync web framework according to [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)

Can be modified async web framework according to [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)

# Performance
For the parameter validation and transformation feature, Pait is mainly responsible for injecting the request data dependency into the `Pydantic` model, and then the `Pydanitc` verifies and transforms the data.

The time consumed by this process <= 0.00005(s), for benchmarks data and subsequent optimization, see [#27](https://github.com/so1n/pait/issues/27)


# Full example
For more complete examples, please refer to [example](https://github.com/so1n/pait/tree/master/example)
