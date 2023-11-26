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
from pait.app.starlette.grpc_route import GrpcGatewayRoute
from pait.app.starlette import AddDocRoute
from pait.util.grpc_inspect.message_to_pydantic import grpc_timestamp_int_handler

# 引入根据Protobuf文件生成的对应代码
from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc
from example.example_grpc.python_example_proto_code.example_proto.book import social_pb2_grpc, manager_pb2_grpc


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
        # 定义路由属性的解析方法，具体见下面说明
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
- stub_list: 支持一个或多个的stub参数，需要注意的是，传入的Stub必须是由Protobuf生成的gRPC Stub类。
- prefix: 生成路由函数的URL前缀，假如`prefix`为`/api`，Stub类的一个gRPC方法对应的URL为`/user.User/get_uid_by_token`，那么生成的URL则是`/api/user.User/get_uid_by_token`。
- title: 生成路由函数名是由title以及一个gRPC方法的方法名决定的，如果一个app实例绑定过个相同的Stub类，则title必须不同。（对于`Tornado`，是通过title和gRPC方法名来定义对应Handler类的名称。）
- parse_msg_desc: 指定要解析msg注释的类型，如果不填则会解析Message对应的Option，如果填入的值为`by_mypy`，则会解析通过`mypy-protobuf`插件生成的pyi文件，如果填入的是一个路径，则会解析对应路径下的Protobuf文件，具体使用方法见:[protobuf_to_pydantic](https://github.com/so1n/protobuf_to_pydantic#22parameter-verification)。
- msg_to_dict: 默认为`google.protobuf.json_format.MessageToDict`。路由函数收到gRPC服务返回的Message对象后，会通过msg_to_dict转为Python的dict对象，再返回json到客户端。
- parse_dict: 默认为空，该参数仅支持`google.protobuf.json_format.ParseDict`以及它的变体。路由函数收到HTTP客户端的请求后会对数据进行校验，然后转为gRPC方法需要的Message对象。
- pait: 用于装饰路由函数的`pait`装饰器对象。
- make_response: 负责把路由函数返回的Dict对象转为对应Web框架的Json响应对象。
- url_handler: 用于更改gRPC自带的URL，默认会把gRPC方法的`.`改为`-`。
- gen_response_model_handle(0.8版本新增): 用于生成路由函数对应的Pait响应对象函数，默认的生成函数如下：
    ```py
    def _gen_response_model_handle(grpc_model: GrpcModel) -> Type[PaitBaseResponseModel]:
        class CustomerJsonResponseModel(PaitJsonResponseModel):
            name: str = grpc_model.response.DESCRIPTOR.name
            description: str = grpc_model.response.__doc__ or ""

            # Rename it,
            # otherwise it will overwrite the existing scheme with the same name when generating OpenAPI documents.
            response_data: Type[BaseModel] = type(
                f"{grpc_model.method}RespModel", (msg_to_pydantic_model(grpc_model.response),), {}
            )

        return CustomerJsonResponseModel
    ```
- request_param_field_dict(0.8版本移除): 指定一个参数名对应的field对象，需要注意的是，这是会应用到所有的Stub对象。
- grpc_timestamp_handler_tuple(0.8版本移除): 该方法支持传入一个(type, callback)的数组，type代表字段对应的类型，callback代表转换方法，字段的类型为Timestamp时会启用。因为gRPC的Timestamp默认情况下只支持字符串转换，所以提供了这个方法来支持其它类型转为gRPC Timestamp对象，比如把int类型转为Timestamp对象，则对应的callback可以写为:
    ```py
    def grpc_timestamp_int_handler(cls: Any, v: int) -> Timestamp:
        t: Timestamp = Timestamp()

        if v:
            t.FromDatetime(datetime.datetime.fromtimestamp(v))
        return t
    ```
## 4.定义路由属性
通过Swagger页面可以发现，UserStub相关的路由函数的url与其它Stub的路由函数不一样，这是因为在Protobuf中定义了UserStub生成路由函数的一些行为，目前支持多种方法来自定义路由属性，下面介绍两种常用方法。

### 4.1.通过Protobuf的Option定义路由的属性(推荐)
!!! note
    0.8以及后续版本才支持本功能


UserStub对应的[user.proto](https://github.com/so1n/pait/blob/master/example/example_grpc/example_proto_by_option/user/user.proto)文件的`service`块，这里通过Option定义了UserStub路由函数的行为，具体如下：
```protobuf
// 引入了pait.api包
import "example_proto_by_option/common/api.proto";

service User {
  // The interface should not be exposed for external use
  rpc get_uid_by_token (GetUidByTokenRequest) returns (GetUidByTokenResult) {
    option (pait.api.http) = {
      not_enable: true, // 定义不解析该函数
      group: "user", // 定义函数的group
      tag: [{name: "grpc-user", desc: "grpc_user_service"}]  // 定义函数的标签
    };
  };
  rpc logout_user (LogoutUserRequest) returns (google.protobuf.Empty) {
    option (pait.api.http) = {
      summary: "User exit from the system",  // 定义函数的简介
      any: {url: "/user/logout"},  // 定义函数的url是什么，any代表具体的HTTP方法由GrpcGateway方法定义，如果要指定HTTP方法为POST,那么需要把any替换为post
      tag: [{name: "grpc-user", desc: "grpc_user_service"}]
    };
  };
  rpc login_user(LoginUserRequest) returns (LoginUserResult) {
    option (pait.api.http) = {
      summary: "User login to system",
      any: {url: "/user/login"},
      tag: [{name: "grpc-user", desc: "grpc_user_service"}]
    };
  };
  rpc create_user(CreateUserRequest) returns (google.protobuf.Empty) {
    option (pait.api.http) = {
      summary: "Create users through the system",
      any: {url: "/user/create"},
      tag: [
        {name: "grpc-user", desc: "grpc_user_service"},
        {name: "grpc-user-system", desc: "grpc_user_service"}
      ]
    };
  };
  rpc delete_user(DeleteUserRequest) returns (google.protobuf.Empty) {
    option (pait.api.http) = {
      desc: "This interface performs a logical delete, not a physical delete",
      any: {url: "/user/delete"},
      tag: [
        {name: "grpc-user", desc: "grpc_user_service"},
        {name: "grpc-user-system", desc: "grpc_user_service"}
      ]
    };
  };
}
```
这份protobuf文件中的第一行引入了`pait.api`包，在使用的过程中建议把该[文件](https://github.com/so1n/pait/blob/master/pait/http/api.proto)下载到对应的目录中，并在自己的Protobuf文件中引入该包。

`pait.api`支持的拓展属性如下:

- group：路由函数对应的group
- tag: 路由函数对应的tag对象
- summary: 路由函数对应的描述
- url: 路由函数对应的url
- enable: 是否要生成对应方法的路由，默认为false
- additional_bindings: 增加一个新的路由映射方法

其中url和additional_bindings的使用方法比较特殊，具体使用方法如下：
```protobuf
service Demo {
  // http方法由GrpcGateway生成，但指定了url为/demo
  rpc demo_request_1 (Empty) returns (Empty) {
    option (pait.api.http) = {
      any: {url: "/demo"},
    };
  };
  rpc demo_request_2 (Empty) returns (Empty) {
    // 指定http方法为post，URL为/demo
    option (pait.api.http) = {
      post: {url: "/demo"},
    };
  };
  rpc demo_request_3 (Empty) returns (Empty) {
    // 指定http方法为post,但是url采用了gRPC生成的url
    option (pait.api.http) = {
      post: {default: true},
    };
  };
  rpc demo_request_4 (Empty) returns (Empty) {
    // 指定http方法为get，URL为/demo
    option (pait.api.http) = {
      get: {url: "/demo"},
    };
    // 额外映射了一个http方法为post,URL为/demo的路由，且指定了对应的desc
    additional_bindings: {
      post: {url: "/demo1"},
      desc: "test additional bindings"
    }
  };
}
```

!!! note
    具体的示例文件见：https://github.com/so1n/pait/tree/master/example/example_grpc/example_proto_by_option
### 4.2.通过Protobuf文件注释定义路由的属性

UserStub对应的[user.proto](https://github.com/so1n/pait/blob/master/example/example_grpc/example_proto/user/user.proto)文件的`service`块，这里通过注释定义了UserStub路由函数的行为，这些注释都是通过`pait: `开头，然后跟着的是一段json数据，具体如下：
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


!!! note
    具体的示例文件见：https://github.com/so1n/pait/tree/master/example/example_grpc/example_proto
## 5.定义Message的属性
在生成路由函数时，`GrpcGatewayRoute`会把方法对应的请求message和响应message解析为路由函数对应的请求和响应对象，这些对象的类型都为`pydantic.BaseModel`，之后`Pait`就可以通过对应的`pydantic.BaseModel`对象来生成文档或者做参数校验。

不过这样生成的`pydantic.BaseModel`对象只有基本的信息，为了能让生成的`pydantic.BaseModel`对象更加的丰富，`Pait`通过[protobuf_to_pydantic](https://github.com/so1n/protobuf_to_pydantic#22parameter-verification)来拓展`pydantic.BaseModel`对象的信息。
### 5.1.通过Protobuf的Option定义Message的属性(推荐)

!!! note
    0.8以及后续版本才支持本功能

该方法通过Protobuf的Option来拓展`pydantic.BaseModel`对象的信息，在使用之前，需要把[文件](https://github.com/so1n/protobuf_to_pydantic/blob/master/p2p_validate/p2p_validate.proto)下载到自己的项目里面，并在自己的Protobuf文件中引用，示例代码如下：
```protobuf
import "example_proto_by_option/common/p2p_validate.proto";

// create user
message CreateUserRequest {
  string uid = 1 [
    (p2p_validate.rules).string.miss_default = true,  // 定义了该字段没有默认值
    (p2p_validate.rules).string.example = "10086",  // 定义字段的示例值为10086
    (p2p_validate.rules).string.title = "UID",  // 定义了字段的Title为UID
    (p2p_validate.rules).string.description = "user union id" // 定义了字段的desc
  ];
  string user_name = 2 [
    (p2p_validate.rules).string.description = "user name",
    (p2p_validate.rules).string.min_length = 1,
    (p2p_validate.rules).string.max_length = 10,
    (p2p_validate.rules).string.example = "so1n"
  ];
  string password = 3 [
    (p2p_validate.rules).string.description = "user password",
    (p2p_validate.rules).string.alias = "pw",
    (p2p_validate.rules).string.min_length = 6,
    (p2p_validate.rules).string.max_length = 18,
    (p2p_validate.rules).string.example = "123456"
  ];
  SexType sex = 4;
}
```

之后生成的文档中关于`CreateUserRequest`的展示如下:
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16525495684371652549568021.png)

这种方式还支持其它的拓展，具体见[protobuf_to_pydantic文档](https://github.com/so1n/protobuf_to_pydantic)
### 5.2.通过Protobuf文件注释定义Message的属性
该方法通过获取Protobuf文件的注释来拓展`pydantic.BaseModel`对象的信息，比如[user.proto](https://github.com/so1n/pait/blob/master/example/example_grpc/example_proto/user/user.proto)文件的`CreateUserRequest`，它的注释如下：
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

// logout user
message LogoutUserRequest {
  string uid = 1;
  // 不解析该字段
  // pait: {"enable": false}
  string token = 2; }
```
之后生成的文档中关于`CreateUserRequest`的展示如下:
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16525495684371652549568021.png)

可以发现Message注释编写的方法与Service的一致，只不过是属性不同，Message支持的属性除了`miss_default`和`enable`外，与`Pait`的Field对象一致，`miss_default`默认为false，如果为true,则代表该字段没有默认值，如果为false，则代表该字段的默认值为Protobuf对应属性的默认值；`enable`默认为True，如果为False，则不会解析该字段。

!!! 支持的属性列表
    - miss_default
    - enable
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
!!! note
    更多使用方法见[protobuf_to_pydantic文档](https://github.com/so1n/protobuf_to_pydantic)
## 6.自定义`Gateway Route`路由函数
虽然提供了一些参数用于`Gateway Route`路由的定制，但是光靠这些参数还是不够的，所以支持开发者通过继承的方式来定义`Gateway Route`路由函数的构造。

比如下述示例的[User.proto](https://github.com/so1n/pait/blob/master/example/example_grpc/example_proto/user/user.proto)文件:
```proto
// 原文件见：https://github.com/so1n/pait/blob/master/example/example_grpc/example_proto_by_option/user/user.proto
// logout user
message LogoutUserRequest {
  string uid = 1;
  // 不解析该字段
  string token = 2 [(p2p_validate.rules).string.enable = false];
}

service User {
  // The interface should not be exposed for external use
  rpc get_uid_by_token (GetUidByTokenRequest) returns (GetUidByTokenResult) {
    option (pait.api.http) = {
      not_enable: true,
      group: "user",
      tag: [{name: "grpc-user", desc: "grpc_user_service"}]
    };
  };
  rpc logout_user (LogoutUserRequest) returns (google.protobuf.Empty) {
    option (pait.api.http) = {
      summary: "User exit from the system",
      any: {url: "/user/logout"},
      tag: [{name: "grpc-user", desc: "grpc_user_service"}]
    };
  };
  rpc login_user(LoginUserRequest) returns (LoginUserResult) {
    option (pait.api.http) = {
      summary: "User login to system",
      any: {url: "/user/login"},
      tag: [{name: "grpc-user", desc: "grpc_user_service"}]
    };
  };
  rpc create_user(CreateUserRequest) returns (google.protobuf.Empty) {
    option (pait.api.http) = {
      summary: "Create users through the system",
      any: {url: "/user/create"},
      tag: [
        {name: "grpc-user", desc: "grpc_user_service"},
        {name: "grpc-user-system", desc: "grpc_user_service"}
      ]
    };
  };
  rpc delete_user(DeleteUserRequest) returns (google.protobuf.Empty) {
    option (pait.api.http) = {
      desc: "This interface performs a logical delete, not a physical delete",
      any: {url: "/user/delete"},
      tag: [
        {name: "grpc-user", desc: "grpc_user_service"},
        {name: "grpc-user-system", desc: "grpc_user_service"}
      ]
    };
  };
}
```
文件中定义的接口中有一个名为`User.get_uid_by_token`的接口，它用于通过token获取uid, 同时拥有校验Token是否正确的效果，这个接口不会直接暴露给外部调用，也就不会通过`Gateway Route`生成对应的HTTP接口。
而其它接口被调用时，需要从Header获取Token并通过gRPC接口`User.get_uid_by_token`进行判断，判断当前请求的用户是否正常，只有校验通过时才会去调用对应的gRPC接口。
同时，接口`User.logout_user`请求体`LogoutUserRequest`的`token`字段被标注为不解析，并通过Herder的获取Token，使其跟其它接口统一。

接下来就通过继承的方法来重新定义`Gateway Route`路由函数的构造：
```Python
from sys import modules
from typing import Callable, Type
from uuid import uuid4

from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2
from pait.util.grpc_inspect.stub import GrpcModel
from pait.util.grpc_inspect.types import Message

class CustomerGrpcGatewayRoute(GrpcGatewayRoute):
    # 继承`GrpcGatewayRoute.gen_route`方法
    def gen_route(
        self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]
    ) -> Callable:

        # 如果不是login_user接口，就走自定义的路由函数
        if grpc_model.method!= "/user.User/login_user":

            async def _route(
                request_pydantic_model: request_pydantic_model_class,  # type: ignore
                token: str = Header.i(description="User Token"),  # 通过Header获取token
                req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),  # 通过Header获取请求id
            ) -> Any:
                # 获取gRPC接口对应的调用函数，需要放在最前，因为它包括了判断channel是否创建的逻辑。
                func: Callable = self.get_grpc_func(method_name)
                request_dict: dict = request_pydantic_model.dict()  # type: ignore
                if method_name == "/user.User/logout_user":
                    # logout_user接口需要一个token参数
                    request_dict["token"] = token
                else:
                    # 其它接口需要通过校验Token来判断用户是否合法
                    result: user_pb2.GetUidByTokenResult = await user_pb2_grpc.UserStub(
                        self.channel
                    ).get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
                    if not result.uid:
                        # 如果不合法就报错
                        raise RuntimeError(f"Not found user by token:{token}")
                # 合法就调用对应的gRPC接口
                request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
                # 添加一个请求ID给gRPC服务
                grpc_msg: Message = await func(request_msg, metadata=[("req_id", req_id)])
                return self._make_response(self.get_dict_from_msg(grpc_msg))

            # 由于request_pydantic_model_class是在父类生成的，所以Pait在兼容延迟注释时获取不到该模块的request_pydantic_model_class值，
            # 所以要把request_pydantic_model_class注入本模块，在下一个版本`GrpcGatewayRoute`会自动处理这个问题。
            modules[_route.__module__].__dict__["request_pydantic_model_class"] = request_pydantic_model_class
            return _route
        else:
            # login_user接口则走自动生成逻辑。
            return super().gen_route(grpc_model, request_pydantic_model_class)
```
之后就可以跟原来使用`GrpcGatewayRoute`的方法一样使用我们新创建的`CustomerGrpcGatewayRoute`，之后就可以看到如下效果：
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16533621713911653362170551.png)
可以看到`/api/user/login`和`/api/user/create`没有什么变化，而`/api/user/logout`需要通过Header获取token和`X-Request-ID`
