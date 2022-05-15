## 隐式引入与显式引入
`pait`对多个框架都提供支持, 如果一个项目中只安装了其中的一个框架, 那么可以使用隐式引入:
```Python3
from pait.app import add_doc_route, load_app, pait

```
但是如果同时安装了多个框架, 那么上面的引入会抛出错误, 建议使用显示引入, 如:
```Python3
from pait.app.starlette import add_doc_route, load_app, pait

```
## data与load_app
- data
由于`pait`的通过一个装饰器来提供功能支持, 所以在编译器启动时, 所有数据都注入到data中, 为后续的文档生成等功能提供支持。
- load_app
data里面有很多路由函数的信息, 但是会缺少关键的参数如`url`, `method`等。
所以还需要使用load_app把相关参数与`pait`装饰器装饰的路由函数数据在data中绑定, 使用方法很简单, 不过要记住, 一定要在注册所有路由后再调用:
  ```Python3
  from starlette.applications import Starlette

  from pait.app.starlette import load_app

  app: Starlette = Starlette()
  # 错误的
  load_app(app)
  # --------
  # app.add_route
  # --------

  # 成功的
  load_app(app)
  ```
## 如何在其它Web框架使用Pait
目前`Pait`还在快速迭代中，所以还是以功能开发为主，如果要在其他尚未支持的框架中使用`Pait`, 或者要对功能进行拓展, 可以参照两个框架进行简单的适配即可.

同步类型的web框架请参照 [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)

异步类型的web框架请参照 [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)

## IDE支持
pait的类型校验和转换以及类型拓展得益于`Pydantic`,同时也从`pydantic`或得到IDE的支持，目前支持`Pycharm`和`Mypy`
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

## 示例代码
更多完整示例请参考[example](https://github.com/so1n/pait/tree/master/example)
## 发行说明
详细的发版说明见[CHANGELOG](https://github.com/so1n/pait/blob/master/CHANGELOG.md)
