
The `Field` object plays a vital role in `Pait`.
In addition to get data sources through the `Field` object, `Pait` can also implement other feature.
However, this chapter only focuses on parameter verification.

## 1.Kind of Field

In addition to the Json mentioned above([Introduction](/1_1_introduction/)), `Field` also has other class, their names and functions are as follows:

- Body: Get the json data of the current request
- Cookie: Get the cookie data of the current request (note that the current cookie data will be converted into a Python dictionary, which means that the key of the cookie cannot be repeated. At the same time, when the Field is a cookie, the type is preferably str)
- File：Get the file object of the current request, which is consistent with the file object of the web framework
- Form：Get the form data of the current request. If there are multiple duplicate Keys, only the first value will be returned
- Json: Get the json data of the current request
- Header: Get the header data of the current request
- Path: Get the path data of the current request, such as `/api/{version}/test`, will get the version data
- Query: Get the data corresponding to the Url parameter of the current request. If there are multiple duplicate keys, only the first value will be returned
- MultiForm：Get the form data of the current request, and return the data list corresponding to the Key
- MultiQuery：Get the data corresponding to the Url parameter of the current request, and return the data list corresponding to the Key

`Field` is easy to use, just use `Field` in the `default` of `<name>:<type>=<default>`, using this code as an example.

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_demo.py"
    ```

!!! note
    In order to ensure that the sample code can run smoothly anywhere, the usage of the `File` field is not demonstrated here.
    For specific usage, please refer to the route function corresponding to `/api/pait-base-field` in the `field_route.py` file in the sample code of different web frameworks.

The sample code demonstrates how to get the request parameters from the request object through different types of `Field` and assemble them into a certain format and return them.
Next, use the `curl` command to a request test:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/demo/12?uid=99&user_name=so1n&multi_user_name=so1n' \
  -H 'accept: application/json' \
  -H 'Cookie: cookie=cookie=test cookie' \
  -H 'Content-Type: multipart/form-data' \
  -F 'form_a=a' \
  -F 'form_b=b' \
  -F 'multi_form_c=string,string'
```

Under normal circumstances, you will see the following output in the terminal:
```json

{
    "code": 0,
    "msg": "",
    "data": {
        "accept": "application/json",
        "form_a": "a",
        "form_b": "b",
        "form_c": [
            "string,string"
        ],
        "cookie": {
            "cookie": "cookie=test cookie"
        },
        "multi_user_name": [
            "so1n"
        ],
        "age": 12,
        "uid": 99,
        "user_name": "so1n",
        "email": "example@xxx.com"
    }
}
```
It can be found from the output results that `Pait` can accurately obtain the corresponding value from the request object through the `Field` type.
## 2.Field feature
From the above example, can see that the `url` does not carry the `email` parameter,
but the `email` in the response value is `example@xxx.com`.
This is because `Pait` will assign the `default` of `Field` to the variable when the `email` value cannot be obtained through the request body.

In addition to the default value, `Field` also has many functions, most of which are derived from `pydantic.Field`.

### 2.1.default
`Pait` gets the default value of the parameter by the `default` attribute of `Field`.
When the `default` attribute of the `Field` is not null and the request body does not have a corresponding value,
`Pait` injects the value of `default` into the corresponding variable.

The following is a simple sample code. Both route functions in the sample code directly return the obtained value `demo_value`.
The `demo` has a default value of the string -- `123`, while the `demo1` has no default value:

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_default_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_default_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_default_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_default_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_default_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_default_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_default_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_default_demo.py"
    ```

After running the code and calling `curl`, can see that the `/api/demo` route returns 123 by default when the `demo_value` parameter is not passed, while the `/api/demo1` route throws an error that the `demo_value` value was not found, as follows.

<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo"
123
> curl "http://127.0.0.1:8000/api/demo1"
Can not found demo_value value
```


When the `demo value` parameter passed is 456, both the `/api/demo` and `/api/demo 1` routes will return 456:
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo?demo_value=456"
456
> curl "http://127.0.0.1:8000/api/demo1?demo_value=456"
456
```

!!! note
    Error handling uses `Tip Exception`. You can learn about the function of `TipException` through [Exception Tip](/1_5_exception/).

### 2.2.default_factory
The feature of `default_factory` is similar to `default`, except that the value received by `default_factory` is a function,
which will be executed  and inject the return value into the variable when the request hits the route function and `Pait` cannot find the required value of the variable from the request object.

Sample code is as follows, the default value of the first route function is the current time, the default value of the second route function is uuid, and their return values are generated each time a request is received.
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_default_factory_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_default_factory_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_default_factory_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_default_factory_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_default_factory_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_default_factory_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_default_factory_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_default_factory_demo.py"
    ```

After running the code and calling `curl`, can find that the results displayed are different each time:

<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo"
2022-02-07T14:54:29.127519
> curl "http://127.0.0.1:8000/api/demo"
2022-02-07T14:54:33.789994
> curl "http://127.0.0.1:8000/api/demo1"
7e4659e18103471da9db91ed4843d962
> curl "http://127.0.0.1:8000/api/demo1"
ef84f04fa9fc4ea9a8b44449c76146b8
```
### 2.3.alias
Normally `Pait` will get data from the request body with the parameter name key,
but some parameter names such as `Content-Type` are not available in `Python`.
In this case, can use `alias` to set an alias for the variable, as shown in the following sample code:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_alias_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_alias_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_alias_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_alias_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_alias_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_alias_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_alias_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_alias_demo.py"
    ```

After running the code and calling the `curl` command,
can find that `Pait` extracts the value of `Content-Type` from the header of the request body and assigns it to the `content type` variable, so the route function can return the value `123` normally:
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo" -H "Content-Type:123"
123
```

### 2.4.GT, GE, LT, LE, and multiple of numeric type checks
`gt`, `ge`, `lt`, `le`, and `multiple_of` all belong to `pydantic`’s numerical type checks.
They are only used for numerical types and have different functions:

- gt：A type that is only used for numeric values. It will check whether the value is greater than this value and also add the `exclusiveMinimum` attribute to the OpenAPI.。
- ge：A type that is only used for numeric values. It will check whether the value is greater than or equal this value and also add the `exclusiveMaximum` attribute to the OpenAPI.。
- lt：A type that is only used for numeric values. It will check whether the value is less than this value and also add the `exclusiveMinimum` attribute to the OpenAPI.。
- le：A type that is only used for numeric values. It will check whether the value is less than or equal this value and also add the `exclusiveMaximum` attribute to the OpenAPI.。
- multiple_of：Only used for numbers, it will check whether the number is a multiple of the specified value。

Usage:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_num_check_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_num_check_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_num_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_num_check_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_num_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_num_check_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_num_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_num_check_demo.py"
    ```

This sample code has only one route function, but it accepts three parameters `demo_value1`, `demo_value2` and `demo_value3`.
They only receive three parameters that are greater than 1 and less than 10, equal to 1 and a multiple of 3 respectively.

After running the code and calling the `curl` command, can find that the first request meets the requirements and gets the correct response result.
However, the values of the `demo_value 1`, `demo_value 2` and `demo_value 3` parameters of the second, third and fourth requests are not within the required range, so `Pait` will generate error message by `Pydantic.Validation Error`, it can be easily seen that the three parameters do not meet the restrictions set by the route function:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=2&demo_value2=1&demo_value3=3"
{"data":[2,1,3]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=11&demo_value2=1&demo_value3=3"
{
    "data": [
        {
            "ctx": {"limit_value": 10},
            "loc": ["query", "demo_value1"],
            "msg": "ensure this value is less than 10",
            "type": "value_error.number.not_lt"
        }
    ]
}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=2&demo_value2=2&demo_value3=3"
{
    "data": [
        {
            "ctx": {"limit_value": 1},
            "loc": ["query", "demo_value2"],
            "msg": "ensure this value is less than or equal to 1",
            "type": "value_error.number.not_le"
        }
    ]
}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=2&demo_value2=1&demo_value3=4"
{
    "data": [
        {
            "ctx": {"multiple_of": 3},
            "loc": ["query", "demo_value3"],
            "msg": "ensure this value is a multiple of 3",
            "type": "value_error.number.not_multiple"
        }
    ]
}
```
### 2.5.Sequence verification: min_items，max_items
`min items` and `max items` both belong to the `Sequence` type check of `pydantic` and are only used for the `Sequence` type. Their functions are different:

- min_items：Only used for `Sequence` type, it will check whether `Sequence` length is greater than or equal to the specified value.。
- max_items： Only used for `Sequence` type, it will check whether `Sequence` length is less than or equal to the specified value.


!!! note

    If using Pydantic version greater than 2.0.0, please use `min_length` and `max_length` instead of `min_items` and `max_items`.

Sample code is as follows,
the route function through the `field.MultiQuery` from the request Url to obtain the parameter `demo_value` of the array and return to the caller,
where the length of the array is limited to between 1 and 2:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_item_check_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_item_check_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_item_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_item_check_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_item_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_item_check_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_item_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_item_check_demo.py"
    ```

As in 2.4, by calling the `curl` command can find that legal parameters will be allowed, and illegal parameters will throw an error:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1"
{"data":[1]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1&demo_value=2"
{"data":[1,2]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1&demo_value=2&demo_value=3"
{
    "data": [
        {
            "loc": [
                "demo_value"
            ],
            "msg": "ensure this value has at most 2 items",
            "type": "value_error.list.max_items",
            "ctx": {
                "limit_value": 2
            }
        }
    ]
}
```
### 2.6.String verification: min_length，max_length，regex
`min_length`, `max_length` and `regex` are all part of `pydantic`'s string type checking,
which is only used for string types and they serve different purposes:

- min_length：Only used for string type, it will check whether the length of the string is greater than or equal to the specified value.
- max_length：Only used for string type, it will check whether the length of the string is less than or equal to the specified value.
- regex：Only used for string types, it will check whether the string conforms to the regular expression.


!!! note

    If using Pydantic version greater than 2.0.0, please use `pattern` instead of `regex`.

The sample code is as follows, the route function needs to obtain a value with a length of 6 and starting with the English letter `u` from the Url:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_string_check_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_string_check_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_string_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_string_check_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_string_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_string_check_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_string_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_string_check_demo.py"
    ```
Run the code and use `curl` to make three requests.
It can be seen from the results that the result of the first request is normal, the result of the second request does not meet the regular expression and the result length of the third request does not meet the requirements:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=u66666"
{"data":"u66666"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=666666"
{"data":[{"loc":["demo_value"],"msg":"string does not match regex \"^u\"","type":"value_error.str.regex","ctx":{"pattern":"^u"}}]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1"
{"data":[{"loc":["demo_value"],"msg":"ensure this value has at least 6 characters","type":"value_error.any_str.min_length","ctx":{"limit_value":6}}]}
```
### 2.7.raw_return

Sample code is as follows,
the route function requires two values, the first value for the entire client passed the Json parameters
and the second value for the client passed the Json parameters in the Key for a value:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_raw_return_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_raw_return_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_raw_return_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_raw_return_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_raw_return_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_raw_return_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_raw_return_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_raw_return_demo.py"
    ```

Run the code and call the `curl` command and can find that the results are as expected:
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo" \
  -X POST -d '{"a": "1", "b": "2"}' \
  --header "Content-Type: application/json"

{"demo_value":{"a":"1","b":"2"},"a":"1"}
```

### 2.8.Custom query cannot find value exception
Under normal circumstances, if there is no data required by `Pait` in the request object,
`Pait` will throw a `Not Found Value Exception` exception.
In addition, `Pait` also supports developers to customize exception handling through `not_value_exception_func`.

For example, the route function in the code below has two variables.
The first variable `demo_value1` does not have any `Field` attributes set.
The second variable `demo_value2` sets the `not_value_exception_func` attribute to `lambda param: RuntimeError(f"not found {param.name} data")`:

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_not_found_exc_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_not_found_exc_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_not_found_exc_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_not_found_exc_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_not_found_exc_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_not_found_exc_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_not_found_exc_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_not_found_exc_demo.py"
    ```

Then run the code and execute the following `curl` command in the terminal:
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo?demo_value1=1&demo_value2=2"
{"data": {"demo_value1": "1", "demo_value2": "2"}}
> curl "http://127.0.0.1:8000/api/demo?demo_value2=2"
{"data": "Can not found demo_value1 value"}
> curl "http://127.0.0.1:8000/api/demo?demo_value1=1"
{"data":"not found demo_value2 data"}
```

Through the output results, can see that the responses to the missing value of `demo_value1` and the missing value of `demo_value2` are different.
The missing value exception message of `demo_value2` is thrown by `lambda param: RuntimeError(f"not found {param.name} data")`.
### 2.8.Other Feature
In addition to the above feature, `Pait` also has other feature, which can be found in the corresponding module documentation:

| Attribute             | document                     | description                                                                                                                                                                                                                     |
|-----------------------|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| links                 | [OpenAPI](/3_1_openapi/)     | support OpenAPI's Link                                                                                                                                                                                                          |
| media_type            | [OpenAPI](/3_1_openapi/)     | OpenAPI Schememedia type。                                                                                                                                                                                                       |
| openapi_serialization | [OpenAPI](/3_1_openapi/)     | Specify the serialization method of OpenAPI Schema.                                                                                                                                                                             |
| example               | [OpenAPI](/3_1_openapi/)     | Example values for documentation, mock requests and responses. values support variables and callable functions such as `datetime.datetim.now`, it is recommended to use [faker](https://github.com/joke2k/faker) used together. |
| description           | [OpenAPI](/3_1_openapi/)     | OpenAPI parameter description                                                                                                                                                                                                   |
| openapi_include       | [OpenAPI](/3_1_openapi/)     | Defines whether this field needs to be processed by OpenAPI. The default is True.                                                                                                                                               |                                                                                          |                                                                                                 |
| extra_param_list      | [Plugin](/5_1_introduction/) | The extra parameter list of the plugin. The default is None.                                                                                                                                                                    |
