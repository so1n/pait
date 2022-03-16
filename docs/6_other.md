## 隐式引入与显式引入
`pait`对多个框架都提供支持, 如果一个项目中只安装了其中的一个框架, 那么可以使用隐式引入:
```Python3
from pait.app import add_doc_route, load_app, pait

```
但是如果同时安装了多个框架, 那么上面的引入会抛出错误, 建议使用显示引入, 如:
```Python3
from pait.app.starlette import add_doc_route, load_app, pait

```
## config, data与load_app
- data
由于`pait`的通过一个装饰器来提供功能支持, 所以在编译器启动时, 所有数据都注入到data中, 为后续的文档生成等功能提供支。
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
- config
config能为`pait`提供一些配置支持, 它需要尽快的初始化, 最佳的初始化位置就是在app初始化之前进行初始化,  同时整个运行时只允许初始化一次
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

参数介绍:

- author: 全局的默认API作者, 如果`@pait`中没有填写author, 会默认调用到`config.author`
- status: 全局的默认API状态, 如果`@pait`中没有填写status, 会默认调用到`config.status`
- enable_mock_response: 决定这次运行是返回正常的响应还是根据`response_model`返回mock响应
- enable_mock_response_filter_fn: 默认支持多个`response_model`, mock响应默认只取第一个`response_model`, 如果觉得这个不符合自己想要的`response_model`, 则可以配置该函数来返回自己想要的结果
- block_http_method_set: 有一些web框架会自动帮忙把一些路由函数添加`HEAD`等请求方法, `pait`是无法识别哪些是框架添加, 哪些是用户自己添加的, 这时可以通过该参数屏蔽一些`method`
- default_response_model_list: 在设计一些API接口时, 通常有一些默认的异常响应, 只需要配置该参数即可应用到全局
- json_type_default_value_dict: 配置json类型的默认值
## 如何在其它Web框架使用Pait
如果要在其他尚未支持的框架中使用pait, 或者要对功能进行拓展, 可以查照两个框架进行简单的适配即可.

同步类型的web框架请参照 [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)

异步类型的web框架请参照 [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)

## IDE支持
pait的类型校验和转换以及类型拓展得益于`Pydantic`,同时也从`pydantic`或得到IDE的支持,目前支持`Pycharm`和`Mypy`
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

## 示例代码
更多完整示例请参考[example](https://github.com/so1n/pait/tree/master/example)
## 发行说明
详细的发版说明见[CHANGELOG](https://github.com/so1n/pait/blob/master/CHANGELOG.md)
