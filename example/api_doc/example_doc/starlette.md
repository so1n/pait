# Pait Doc
<details><summary>Group: check_resp</summary>

### Name: async_text_response_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 383">async_text_response_route</abbr>|    |
- Path: /api/text-resp
- Method: GET,HEAD
- Request:
- Response:

    - TextRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|text/plain|text response|
        - Header
            {'X-Example-Type': 'text'}

### Name: html_response_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 391">html_response_route</abbr>|    |
- Path: /api/html-resp
- Method: GET,HEAD
- Request:
- Response:

    - HtmlRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|text/html|html response|
        - Header
            {'X-Example-Type': 'html'}

### Name: file_response_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 399">file_response_route</abbr>|    |
- Path: /api/file-resp
- Method: GET,HEAD
- Request:
- Response:

    - FileRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/octet-stream|file response|
        - Header
            {'X-Example-Type': 'file'}

</details><details><summary>Group: links</summary>

### Name: login_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 416">login_route</abbr>|    |
- Path: /api/login
- Method: POST
- Request:
    - Body Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |password|string|**`Required`**| |password||
        |uid|string|**`Required`**| |user id||
- Response:

    - LoginRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|login response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.token|string|**`Required`**| | ||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "token": ""
              }
            }
            ```


### Name: get_user_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 429">get_user_route</abbr>|    |
- Path: /api/user
- Method: GET,HEAD
- Request:
    - Header Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |token|string| | |token||
- Response:

    - SuccessRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```


</details><details><summary>Group: other</summary>

### Name: ~~raise_tip_route~~



**Desc**:test pait raise tip

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#DC143C>abandoned</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 69">raise_tip_route</abbr>|    |
- Path: /api/raise-tip
- Method: POST
- Request:
    - Header Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |content__type|string|**`Required`**| |Content-Type||
- Response:

    - SimpleRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`Required`**| |success result||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: post_route



**Desc**:Test Method:Post Pydantic Model

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 82">post_route</abbr>|    |
- Path: /api/post
- Method: POST
- Request:
    - Body Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**|123|user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**|so1n|user name|[`maxLength:4`], [`minLength:2`]|
    - Header Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| |Content-Type||
- Response:

    - UserSuccessRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|99| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.content_type|string|**`Required`**| |content-type||
            |data.uid|integer|666| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|mock_name| |user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "age": 99,
                "sex": "man",
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: pait_model_route



**Desc**:Test pait model

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 276">pait_model_route</abbr>|    |
- Path: /api/pait-model
- Method: POST
- Request:
    - Body Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |user_info|object|**`Required`**| | |[`properties:{'user_name': {'title': 'User Name', 'description': 'user name', 'maxLength': 4, 'minLength': 2, 'type': 'string'}, 'age': {'title': 'Age', 'description': 'age', 'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'type': 'integer'}}`], [`required:['user_name', 'age']`]|
    - Header Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |user-agent|string|**`Required`**| |user agent||
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- Response:

    - SimpleRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`Required`**| |success result||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: depend_contextmanager_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 282">depend_contextmanager_route</abbr>|    |
- Path: /api/check_depend_contextmanager
- Method: GET,HEAD
- Request:
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- Response:

    - SuccessRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: depend_async_contextmanager_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 315">depend_async_contextmanager_route</abbr>|    |
- Path: /api/check_depend_async_contextmanager
- Method: GET,HEAD
- Request:
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- Response:

    - SuccessRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: pre_depend_contextmanager_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 291">pre_depend_contextmanager_route</abbr>|    |
- Path: /api/check_pre_depend_contextmanager
- Method: GET,HEAD
- Request:
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- Response:

    - SuccessRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: pre_depend_async_contextmanager_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 303">pre_depend_async_contextmanager_route</abbr>|    |
- Path: /api/check_pre_depend_async_contextmanager
- Method: GET,HEAD
- Request:
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- Response:

    - SuccessRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details><details><summary>Group: plugin</summary>

### Name: check_json_plugin_route



**Desc**:Test json plugin by resp type is dict

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 437">check_json_plugin_route</abbr>|    |
- Path: /api/check-json-plugin
- Method: GET,HEAD
- Request:
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`Required`**| |user email||
            |data.uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "email": ""
              }
            }
            ```


### Name: check_json_plugin_route1



**Desc**:Test json plugin by resp type is typed dict

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 478">check_json_plugin_route1</abbr>|    |
- Path: /api/check-json-plugin-1
- Method: GET,HEAD
- Request:
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`Required`**| |user email||
            |data.uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "email": ""
              }
            }
            ```


</details><details><summary>Group: user</summary>

### Name: depend_route



**Desc**:Test Method:Post request, Pydantic Model

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 101">depend_route</abbr>|    |
- Path: /api/depend
- Method: POST
- Request:
    - Body Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
    - Header Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |user-agent|string|**`Required`**| |user agent||
- Response:

    - SimpleRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`Required`**| |success result||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: field_default_factory_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 126">field_default_factory_route</abbr>|    |
- Path: /api/field-default-factory
- Method: POST
- Request:
    - Body Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |data_dict|object|**`Required`**| |test default factory||
        |data_list|array|**`Required`**| |test default factory|[`items:{'type': 'string'}`]|
        |demo_value|integer|**`Required`**| |Json body value not empty||
- Response:

    - SimpleRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`Required`**| |success result||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: pait_base_field_route



**Desc**:Test the use of all BaseField-based

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 141">pait_base_field_route</abbr>|    |
- Path: /api/pait-base-field/{age}
- Method: GET,HEAD
- Request:
    - Cookie Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |cookie|object|**`Required`**| |cookie||
    - File Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |upload_file|PydanticUndefined|**`Required`**| |upload file||
    - Form Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |a|string|**`Required`**| |form data||
        |b|string|**`Required`**| |form data||
    - Multiform Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |c|array|**`Required`**| |form data|[`items:{'type': 'string'}`]|
    - Multiquery Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |multi_user_name|array|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 4}`]|
    - Path Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |email|string|example@xxx.com| |user email||
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - SimpleRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`Required`**| |success result||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: same_alias_route

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 115">same_alias_route</abbr>|    |
- Path: /api/same-alias
- Method: GET,HEAD
- Request:
    - Header Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |token|string| | | ||
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |token|string| | | ||
- Response:

    - SimpleRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`Required`**| |success result||
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: mock_route



**Desc**:Test gen mock response

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 245">mock_route</abbr>|    |
- Path: /api/mock/{age}
- Method: GET,HEAD
- Request:
    - Multiquery Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |multi_user_name|array|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 4}`]|
    - Path Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |email|string|example@xxx.com| |user email||
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel2

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`Required`**|99|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`Required`**|example@so1n.me|user email||
            |data.multi_user_name|array|**`Required`**|('mock_name',)|user name|[`maxLength:4`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 4}`]|
            |data.uid|integer|**`Required`**|666|user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`Required`**|mock_name|user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "multi_user_name": [],
                "sex": "man",
                "age": 99,
                "email": "example@so1n.me"
              }
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CbvRoute.get



**Desc**:Text cbv route get

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 327">CbvRoute.get</abbr>|    |
- Path: /api/cbv
- Method: get
- Request:
    - Header Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| | ||
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|99| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.content_type|string|**`Required`**| |content-type||
            |data.uid|integer|666| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|mock_name| |user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "age": 99,
                "sex": "man",
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CbvRoute.post



**Desc**:test cbv post method

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 354">CbvRoute.post</abbr>|    |
- Path: /api/cbv
- Method: post
- Request:
    - Body Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
    - Header Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| | ||
- Response:

    - UserSuccessRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|99| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.content_type|string|**`Required`**| |content-type||
            |data.uid|integer|666| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|mock_name| |user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "age": 99,
                "sex": "man",
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: check_param_route



**Desc**:Test check param

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 182">check_param_route</abbr>|    |
- Path: /api/check-param
- Method: GET,HEAD
- Request:
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |alias_user_name|string| | |user name|[`maxLength:4`], [`minLength:2`]|
        |birthday|string| | |birthday||
        |email|string|example@xxx.com| |user email||
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string| | |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel2

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`Required`**|99|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`Required`**|example@so1n.me|user email||
            |data.multi_user_name|array|**`Required`**|('mock_name',)|user name|[`maxLength:4`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 4}`]|
            |data.uid|integer|**`Required`**|666|user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`Required`**|mock_name|user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "multi_user_name": [],
                "sex": "man",
                "age": 99,
                "email": "example@so1n.me"
              }
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: check_response_route



**Desc**:Test test-helper check response

- API Info

    |Author|Status|Func|Summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 217">check_response_route</abbr>|    |
- Path: /api/check-resp
- Method: GET,HEAD
- Request:
    - Query Param

        |Param Name|Type|Default|Example|Desc|Other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`Required`**| |user email||
            |data.uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "email": ""
              }
            }
            ```

    - FailRespModel

        - Response Info

            |Status Code|Media Type|Desc|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |Param Name|Type|Default|Example|Desc|Other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details>
