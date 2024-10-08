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

# pait

Pait is an api tool that can be used in any python web framework, the features provided are as follows:
- [x] Integrate into the Type Hints ecosystem to provide a safe and efficient API interface coding method.
 - [x] Automatic verification and type conversion of request parameters (depends on `Pydantic` and `inspect`, currently supports `Pydantic` V1 and V2 versions).
 - [x] Automatically generate openapi files and support UI components such as `Swagger`,`Redoc`,`RapiDoc` and `Elements`.
 - [x] TestClient support, response result verification of test cases。
 - [x] Plugin expansion, such as parameter relationship dependency verification, Mock response, etc.。
 - [x] gRPC GateWay (After version 1.0, this feature has been migrated to [grpc-gateway](https://github.com/python-pai/grpc-gateway))
 - [ ] Automated API testing
 - [ ] WebSocket support
 - [ ] SSE support

> Note:
>
> - mypy check 100%
>
> - python version >= 3.8 (support postponed annotations)



# Installation
```Bash
pip install pait
```

# Simple Example
```python
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body
from pait.openapi.doc_route import add_doc_route
from pydantic import BaseModel, Field


class ResponseModel(BaseModel):
    """demo response"""
    uid: int = Field()
    user_name: str = Field()


@pait(response_model_list=[ResponseModel])
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
The main operating principle of `Pait` is to convert the function signature of the route function into `Pydantic Model` through the reflection mechanism when the program is started,
and then verify and convert the request parameters through `Pydantic Model` when the request hits the route.

These two stages are all automatically handled internally by `Pait`.
The first stage only slightly increases the startup time of the program, while the second stage increases the response time of the routing, but it only consumes 0.00005(s) more than manual processing.
The specific benchmark data and subsequent optimization are described in [#27](https://github.com/so1n/pait/issues/27).

# Example
For more complete examples, please refer to [example](https://github.com/so1n/pait/tree/master/example)
