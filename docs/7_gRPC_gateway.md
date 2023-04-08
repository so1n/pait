## 1.介绍
gRPC基于HTTP/2.0进行通信，理论上很容易自动转换成一个RESTful接口，所以`Go gRPC`很容易的就能实现`gRPC GatwWay`功能，如[grpc-gateway](https://github.com/grpc-ecosystem/grpc-gateway)。但是`Python gRPC`却很难做到，因为它不像`Go gRPC`一样是使用Go语言编写的库，而是用C语言编写的，同时`Python gRPC`提供的API比较少，所以`Python`要写一个转发HTTP请求到gRPC服务比较麻烦，而`Pait`提供的`gRPC GateWay`功能可以为开发者以最小的代码实现一个简单的`gRPC Gateway`。

!!! note
    `Pait`提供的`gRPC GateWay`功能实际上是类似一个代理服务，它会把HTTP客户端发送的请求转为对应的Msg对象，再通过channel发送给gRPC服务端，最后把gRPC服务端返回的Msg对象转为框架对应的Json响应返回给HTTP客户端。

## 2.使用
`gRPC GateWay`的使用非常简单， 代码例子如下：

```py
from typing import Any
import grpc
from starlette.applications import Starlette
from pait.grpc.gateway import GrpcGatewayRoute
from pait.app.starlette import AddDocRoute

# 引入根据Protobuf文件生成的对应代码
from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2_grpc
from example.grpc_common.python_example_proto_code.example_proto.book import social_pb2_grpc, manager_pb2_grpc


def create_app() -> Starlette:
    app: Starlette = Starlette()
    # 为app注册UserStub,BookSocialStub和BookManagerStub的路由函数
    grpc_gateway_route: GrpcGatewayRoute = GrpcGatewayRoute(
        app,
        # 传入对应的Stub类
        user_pb2_grpc.UserStub,
        social_pb2_grpc.BookSocialStub,
        manager_pb2_grpc.BookManagerStub,
        # 指定url开头
        prefix="/api",
        # 指定生成的路由函数名的开头
        title="Grpc",
        # 见下面说明
        parse_msg_desc="by_mypy",
    )

    def _before_server_start(*_: Any) -> None:
        # 启动时注册对应的channel,这样注册的路由函数在接收请求时可以把参数通过grpc.channel传给grpc服务端
        grpc_gateway_route.init_channel(grpc.aio.insecure_channel("0.0.0.0:9000"))

    async def _after_server_stop(*_: Any) -> None:
        # 关闭时关闭建立的channel
        await grpc_gateway_route.channel.close()

    app.add_event_handler("startup", _before_server_start)
    app.add_event_handler("shutdown", _after_server_stop)

    # 注册文档路由，这样可以方便的看出GrpcGateWayRoute的路由函数是什么
    AddDocRoute(prefix="/api-doc", title="Pait Api Doc").gen_route(app)
    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(
        apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})]
    )

    uvicorn.run(create_app(), log_level="debug")
```
运行代码后，访问对应的链接[http://127.0.0.1:8000/api-doc/swagge](http://127.0.0.1:8000/api-doc/swagge)就可以看到如下页面：
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16525440344511652544033702.png)

页面中的API都是`GrpcGatewayRoute`通过解析Protobuf生成的Stub类生成的，具体的Protobuf文件可以访问[example_proto](https://github.com/so1n/pait/tree/master/example/example_grpc/example_proto)了解。

!!! note
    需要注意的是，如果不通过`GrpcGatewayRoute`的`init_channel`方法指定grpc.channel，那么路由函数收到请求后无法把该请求转成grpc请求发送给对应的gRPC服务。

## 3.参数介绍
`GrpcGatewayRoute`提供的参数都会应用到所有Stub中，如果每个Stub需要应用不同的参数，则可以分开注册Stub，`GrpcGatewayRoute`支持的参数如下:

- app: 必填，且必须是对应的app实例，`GrpcGatewayRoute`会把Stub生成的路由函数注册到对应的app实例中。
- stub: 支持一个或多个的stub参数，需要注意的是，传入的Stub必须是由Protobuf生成的gRPC Stub类。
- prefix: 生成路由函数的URL前缀，假如`prefix`为`/api`，Stub类的一个gRPC方法对应的URL为`/user.User/get_uid_by_token`，那么生成的URL则是`/api/user.User/get_uid_by_token`。
- title: 生成路由函数名是由title以及一个gRPC方法的方法名决定的，如果一个app实例绑定过个相同的Stub类，则title必须不同。（对于`Tornado`，是通过title和gRPC方法名来定义对应Handler类的名称。）
- parse_msg_desc: 指定要解析msg注释的类型，如果填入的值为`by_mypy`，则会解析通过`mypy-protobuf`插件生成的pyi文件，如果填入的是一个路径，则会解析对应路径下的Protobuf文件。
- msg_to_dict: 默认为`google.protobuf.json_format.MessageToDict`。路由函数收到gRPC服务返回的Message对象后，会通过msg_to_dict转为Python的dict对象，再返回json到客户端。
- parse_dict: 默认为空，该参数仅支持`google.protobuf.json_format.ParseDict`以及它的变体。路由函数收到HTTP客户端的请求后会对数据进行校验，然后转为gRPC方法需要的Message对象。
- pait: 用于装饰路由函数的`pait`装饰器对象。
- make_response: 负责把路由函数返回的Dict对象转为对应Web框架的Json响应对象。
- url_handler: 用于更改gRPC自带的URL，默认会把gRPC方法的`.`改为`-`。
- request_param_field_dict: 指定一个参数名对应的field对象，需要注意的是，这是会应用到所有的Stub对象。
- grpc_timestamp_handler_tuple: 该方法支持传入一个(type, callback)的数组，type代表字段对应的类型，callback代表转换方法，字段的类型为Timestamp时会启用。因为gRPC的Timestamp默认情况下只支持字符串转换，所以提供了这个方法来支持其它类型转为gRPC Timestamp对象，比如把int类型转为Timestamp对象，则对应的callback可以写为:
```py
def grpc_timestamp_int_handler(cls: Any, v: int) -> Timestamp:
    t: Timestamp = Timestamp()

    if v:
        t.FromDatetime(datetime.datetime.fromtimestamp(v))
    return t
```
## 4.通过Protobuf文件注释定义路由的属性
通过Swagger页面可以发现，UserStub相关的路由函数的url与其它Stub的路由函数不一样，这是因为在Protobuf中通过注释定义了UserStub生成路由函数的一些行为。比如UserStub对应的[user.proto](https://github.com/so1n/pait/blob/master/example/example_grpc/example_proto/user/user.proto)文件的`service`块，这里通过注释定义了UserStub路由函数的行为，这些注释都是通过`pait: `开头，然后跟着的是一段json数据，具体如下：
```proto
// 定义了整个User服务生成的路由函数的group都是user, tag都是grpc-user(后面跟着的grpc_user_service是对应的文档描述)
// pait: {"group": "user", "tag": [["grpc-user", "grpc_user_service"]]}
service User {
  // 定义不要生成get_uid_by_token的路由函数
  // pait: {"enable": false}
  rpc get_uid_by_token (GetUidByTokenRequest) returns (GetUidByTokenResult);
  // 定义logout_user 函数的summary和url
  // pait: {"summary": "User exit from the system", "url": "/user/logout"}
  rpc logout_user (LogoutUserRequest) returns (google.protobuf.Empty);
  // pait: {"summary": "User login to system", "url": "/user/login"}
  rpc login_user(LoginUserRequest) returns (LoginUserResult);
  // pait: {"tag": [["grpc-user", "grpc_user_service"], ["grpc-user-system", "grpc_user_service"]]}
  // pait: {"summary": "Create users through the system", "url": "/user/create"}
  rpc create_user(CreateUserRequest) returns (google.protobuf.Empty);
  // pait: {"url": "/user/delete", "tag": [["grpc-user", "grpc_user_service"], ["grpc-user-system", "grpc_user_service"]]}
  // pait: {"desc": "This interface performs a logical delete, not a physical delete"}
  rpc delete_user(DeleteUserRequest) returns (google.protobuf.Empty);
}
```
这份文件的注释都是通过`pait: `开头，然后跟着一段json数据，目前解析方法并不是非常的智能，所以不支持换行，如果定义的属性过多则需要另起一行注释，这行注释也需要以`pait: `开头，同时注释一定要写在对应方法的前面。如果service定义了对应的属性，而rpc方法没有定义，则在生产rpc方法对应的路由时会采用service定义的属性。

目前支持的可定义的属性如下:

- name: 路由函数的名称，默认为空字符串
- tag: 路由函数对应的tag列表，列表内必须是一个元祖，分别为tag的名和tag的描述
- group：路由函数对应的group
- summary: 路由函数对应的描述
- url: 路由函数对应的url
- enable: 是否要生成对应方法的路由，默认为false

## 5.通过Protobuf文件注释定义Message的属性
在生成路由函数时，`GrpcGatewayRoute`会把方法对应的请求message和响应message解析为路由函数对应的请求和响应对象，这些对象的类型都为`pydantic.BaseModel`，之后`Pait`就可以通过对应的`pydantic.BaseModel`对象来生成文档或者做参数校验。

目前也是通过注释来定义Message的每个字段对应的Field对象属性，不过`Python`的gRPC在通过Protobuf文件生成对应的Python对象时，并不会把对应的注释带过来，所以`GrpcGatewayRoute`需要通过`parse_msg_desc`参数来知道要解析的来源文件，不过这些来源文件的注释最终都是通过Protobuf文件的注释生成的，比如[user.proto](https://github.com/so1n/pait/blob/master/example/example_grpc/example_proto/user/user.proto)文件的`CreateUserRequest`，它的注释如下：
```proto
message CreateUserRequest {
  // 通常Protobuf的Message都有默认值，如果指定miss_default为true，则不会使用gRPC的默认值
  // pait: {"miss_default": true, "example": "10086", "title": "UID", "description": "user union id"}
  string uid = 1;
  // pait: {"description": "user name"}
  // pait: {"default": "", "min_length": 1, "max_length": "10", "example": "so1n"}
  string user_name = 2;
  // pait: {"description": "user password"}
  // pait: {"alias": "pw", "min_length": 6, "max_length": 18, "example": "123456"}
  string password = 3;
  SexType sex = 4;
}
```
之后生成的文档中关于`CreateUserRequest`的展示如下:
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16525495684371652549568021.png)

可以发现Message注释编写的方法与Service的一致，只不过是属性不同，Message支持的属性除了`miss_default`外，与`Pait`的Field对象一致，`miss_default`默认为false，如果为true,则代表该字段没有默认值，如果为false，则代表该字段的默认值为Protobuf对应属性的默认值。

!!! 支持的属性列表
    - miss_default
    - example
    - alias
    - title
    - description
    - const
    - gt
    - ge
    - lt
    - le
    - min_length
    - max_length
    - min_items
    - max_items
    - multiple_of
    - regex
    - extra
