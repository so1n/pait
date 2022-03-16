`Pait`对于单元测试有一个简单的支持，使开发者能像调用函数一样去编写测试用例，并自动从`response_modle_list`中挑选一个最合适的`response_model`与响应结果进行简单的校验，从而减少开发者编写测试用例的代码量。

## 使用方法
以[example.starlette_example.py.post_route](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py#L104)为例子：
```Python
@other_pait(
    status=PaitStatus.release,
    tag=(tag.user_tag, tag.post_tag),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
async def post_route(
    model: UserModel = Body.i(raw_return=True),
    other_model: UserOtherModel = Body.i(raw_return=True),
    sex: SexEnum = Body.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
) -> JSONResponse:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return JSONResponse({"code": 0, "msg": "", "data": return_dict})
```
这是一个被`Pait`装饰的函数的接口函数，接下来就可以通过如下调用，来完成一个测试用例：
```Python
class TestStarlette:
    def test_post(self, client: TestClient) -> None:
        StarletteTestHelper(
            client,
            starlette_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        ).json()
```
在这个测试用例中， 开发者只需要传入框架对应的测试客户端，路由对应的函数，以及一些请求参数即可，最后通过`json`方法获取到该接口响应的数据。

在这段调用逻辑中，`TestHelper`自动发现了路由函数的`Url`和请求方法，所以调用`json`的时候`TestHelper`自动发起了`post`请求，
然后把响应Body序列化为`Python`的`dict`对象返回， 但是当该路由函数绑定了多个请求方法时，`TestHelper`则无法自动执行，需要手动指定对应的方法来发起请求，
比如下面的代码:
```Python
class TestStarlette:
    def test_post(self, client: TestClient) -> None:
        StarletteTestHelper(
            client,
            starlette_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        ).json(method="post")
```

此外，在编写测试用例时，可能会状态码，`Header`之类的数据进行校验，这时需要一个响应对象
，`TestHelper`支持通过指定对应的Http请求方法名来调用，最后返回对应测试客户端的Response:
```Python
class TestStarlette:
    def test_post(self, client: TestClient) -> None:
        response: Response = StarletteTestHelper(
            client,
            starlette_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        ).post()
        response.json()
```
虽然这种情况下使用`TestHelper`和对应的测试客户端没有太大的差别，但是`TestHelper`的内会在获取到路由函数的响应后
把响应数据放入`Pait`装饰器中`response_model_list`填写的`response_model`进行校验，如果检查到HTTP状态码，Header，Body三者中有一个不符合条件就会抛出错误，中断测试用例。

## 参数介绍
`TestHelper`的参数分为初始化参数，请求参数，响应结果参数3种，初始化参数有3个，分别为：

- client: 测试框架对应的客户端
- func: 路由函数
- pait_dict: `Pait`针对路由函数生成的一个数据结构，该参数可以不填，`TestHelper`在初始化时会自动补全。

请求参数有多个，这些参数可能对于大多数开发者来说平平无奇，但对于使用`Tornado`之类的没对测试客户端做过多封装的框架的开发者则能提供了一些便利，这些参数有:

- body_dict: 发起请求时的Json数据。
- cookie_dict: 发起请求时的cookie数据。
- file_dict: 发起请求时的file数据。
- form_dict: 发起请求时的form数据。
- header_dict: 发起请求时的header数据。
- path_dict: 发起请求时的path数据。
- query_dict: 发起请求时的query数据。

除此之外，`TestHelper`还有3个与HTTP响应结果的Body校验相关的参数，默认情况下，响应结果的Body会与开发者填写的`response_model`的`response_data`进行校验，
如果Body的类型属于Json，`TestHelper`除了会对每个字段的类型进行校验外，还会对字段差异进行校验，如果出现差异则会报错，比如下面a变量是我们定义的`response_demo`数据结构，b变量是响应体的数据结构:
```Python
a = {
    "a": 1,
    "b": {
        "c": 3
    }
}
b = {
    "a": 2,
    "b": {
        "c": 3,
        "d": 4
    }
}
```
`TestHelper`检测到b变量多出来一个结构`b['b']['d']`，所以b变量并不是一个合法的响应体，`TestHelper`直接抛出错误，
不过也可以设置参数`strict_inspection_check_json_content`的值为`False`，这样只会校验出现在`response_model`的字段的类型是否合法以及是否缺少对应的字段，不会检查多出的字段。

`TestHelper`另外两个参数作用如下:

- target_pait_response_class:
    该参数可以传入一个指定的`response_model`，这样`TestHelper`就会从`response_model_list`中筛选出一批符合条件的`response_model`来进行校验。
- find_coro_response_model:
    该参数默认为`False`，这种情况下`TestHelper`会从筛选后的`response_model_list`中自动挑选与响应体最符合的`response_model`来进行校验，如果设置为`True`，那么`TestHelper`只会从筛选后的`response_model_list`中挑出第一个属性`is_core`为`True`的`response_model`来进行校验。
