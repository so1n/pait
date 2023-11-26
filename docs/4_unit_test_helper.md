
Currently, `Pait` provides a simple unit test support through `TestHelper`,
which runs tests by automatically adding URLs, HTTP methods and other parameters by route functions.
And when getting the result, it will get the most matching response model from `response_modle_list` for simple validation,
thus reducing the amount of code required for developers to write test cases.

## 1.Usage of TestHelper
The sample code used this time is to expand the sample code on the home page,
the main change is to add a parameter named `return_error_resp` in the route function,
when `return_error_resp` is `True` it will return a response that does not match the response model,
the code is as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py" hl_lines="21 25"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py::31"
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py" hl_lines="23 27"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py::32"

    import uvicorn
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py" hl_lines="22 26"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py::32"

    import uvicorn
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py" hl_lines="22 27"
    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py::33"
    app.listen(8000)

    from tornado.ioloop import IOLoop
    IOLoop.instance().start()
    ```

Then can write test cases with `TestHelper`,
first need to import `TestHelper` and the test client for the corresponding web framework and also initialize the test framework:.
=== "Flask"

    !!! note

        Since `Flask` automatically registers the `OPTIONS` method in the route that registers the `POST` method,
        which interferes with the autodiscovery of `TestHelper`'s HTTP methods,
        need to block the `OPTIONS` method with `apply_block_http_method_set`.

    ```py linenums="33" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:35:66"
    ```

=== "Starlette"

    !!! note

        When using `with TestClient(app) as client`, `Starlette` automatically calls the app's `startup` and `shutdown` methods, which is a good habit to get into when using `with TestClient(app) as client`, even though it's not used in this test case.

    ```py linenums="38" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:37:51"
    ```

=== "Sanic"

    ```py linenums="39" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:37:50"
    ```

=== "Tornado"

    !!! note

        Currently I don't know how to execute `Tornado` test cases via `Pytest`, so I used `Tornado`'s `AsyncHTTPTestCase` for initialization. If you know how to execute `Tornado` test cases via `Pytest`, feel free to give feedback via [issue](https://github.com/so1n/pait/issues).

    ```py linenums="38" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:37:51"
    ```
After writing the initialization code for the test case, it is time to write the test case code,
first it will be demonstrated how to write a test case through `TestHelper` with the following code:
=== "Flask"

    ```py linenums="65" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:69:75"
    ```

=== "Starlette"

    ```py linenums="50" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:54:60"
    ```

=== "Sanic"

    ```py linenums="50" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:53:59"
    ```

=== "Tornado"

    ```py linenums="50" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py"
    class TestTornado(AsyncHTTPTestCase):
        ...

    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:53:59"
    ```


In this test case, `TestHelper` will be initialized,
`TestHelper` initialization requires the Web framework corresponding to the test client,
the route function, as well as the route function of some of the request parameters,
after the initialization is complete, you can get the request response through the `TestHelper`.

While executing the test, `TestHelper` automatically discovers the `URL` and HTTP method of the route function.
So when calling the `json` method, `TestHelper` will automatically initiate a `post` request and gets the response result.
Then it serializes the response Body into a `Python` `dict` object and returns it.
However, when the route function is bound to more than one request method,
`TestHelper` will not be able to do this automatically,
and need to specify the corresponding HTTP method when calling the `json` method, using the following method:

=== "Flask"

    ```py linenums="74" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:78:84"
    ```

=== "Starlette"

    ```py linenums="59" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:63:69"
    ```

=== "Sanic"

    ```py linenums="59" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:62:68"
    ```

=== "Tornado"

    ```py linenums="58" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py"
    class TestTornado(AsyncHTTPTestCase):
        ...

    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:61:67"
    ```

In addition, when writing test cases, may need a response object, rather than response data,
in order to validate data such as status codes, `Header`, etc.
This can be done by calling the `HTTP` method of the `TestHelper` and getting the response object.
The following code makes a request to the route function via the `post` method and returns the response object of the Web framework's test client,
which is then asserted:
=== "Flask"

    ```py linenums="83" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:87:95"
    ```

=== "Starlette"

    ```py linenums="68" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:72:80"
    ```

=== "Sanic"

    ```py linenums="68" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:71:79"
    ```

=== "Tornado"

    ```py linenums="66" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py"
    class TestTornado(AsyncHTTPTestCase):
        ...

    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:69:77"
    ```
Although in this case `TestHelper` is not much different from the way it is used with the Web framework's corresponding test client.
However, when `TestHelper` gets the response from the route function,
it will pick the best matching response model from the `response_model_list` of the route function.
If one of the response object's HTTP status code, header and response data does not match the response model,
an error is thrown and the test case is aborted, for example:
=== "Flask"

    ```py linenums="92" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:96:104"
    ```

=== "Starlette"

    ```py linenums="77" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:81:89"
    ```

=== "Sanic"

    ```py linenums="77" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:80:89"
    ```

=== "Tornado"

    ```py linenums="76" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py"
    class TestTornado(AsyncHTTPTestCase):
        ...

    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:79:85"
    ```

After executing the test case,
`TestHelper` will find that the response result of the route function does not match the response model of the route function,
then it will throw an exception, interrupt the test case and output the result as follows:
```bash
> raise exc
E pait.app.base.test_helper.CheckResponseException: maybe error result:
E >>>>>>>>>>
E check json content error, exec: 2 validation errors for ResponseModel
E uid
E   field required (type=value_error.missing)
E user_name
E   field required (type=value_error.missing)
E
E >>>>>>>>>>
E by response model:<class 'docs_source_code.unit_test_helper.flask_test_helper_demo.DemoResponseModel'>
```
The output shows that the exception thrown is `CheckResponseException`. Meanwhile, according to the exception message,
can understand that the response model for this validation is `DemoResponseModel`,
and it found that the response data is missing the `uid` field and `user_name` field during the validation process.


## 2.Parameter introduction
The parameters of `TestHelper` are divided into three types:
initialization parameters, request-related parameters, and response-related result parameters.
Among them, the initialization parameters are described as follows:

| Parameters | Description                           |
|------------|---------------------------------------|
| client     | The test client for the Web framework |
| func       | The route function to be tested     |

There are multiple request parameters, which for most web frameworks encapsulate a layer of calls,
but for using frameworks such as `Tornado` that don't encapsulate the test client much,
request parameters provide some convenience, and these parameters are described as follows:


- body_dict: Json data of the request.
- cookie_dict: Cookie data of the request.
- file_dict: File data of the request.
- form_dict: Form data of the request.
- header_dict: Header data of the request.
- path_dict: Path data of the request.
- query_dict: Query data of the request.

In addition to this, `TestHelper` has some parameters related to response result validation, such as `strict_inspection_check_json_content`.
By default, the `strict_inspection_check_json_content` parameter has a value of True,
which will allow `TestHelper` to perform strict checks on the data structure of the response result, as in the following example:
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
In this example, `a` and `b` have different data structures,
where the `a` represents the data structure of the response model and the `b` is the data structure of the response body.
When `TestHelper` performs the validation, it will throw an error because it detects an extra structure `['b']['d']` in the `b`.
However, it is possible to set the parameter `strict_inspection_check_json_content` to `False`,
so that `TestHelper` will only validate fields that appear in the response model, and will not check fields outside the response model.

In addition to the above, `TestHelper` has several other parameters, as follows:


|parameter|description|
|---|---|
|target_pait_response_class|If the value is not null, then `TestHelper` will filter a batch of eligible `response_models` from the `response_model_list` by `target_pait_response_class` to perform the calibration. This value is usually the parent class of the response model, and the default value of `None` means no match. |
|enable_assert_response|Indicates whether `TestHelper` will assert the response result, default value is True. |
