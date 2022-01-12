# Pait Doc
<details><summary>Group: check_resp</summary>

### Name: text_response_route



**Desc**:test return test response

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:example/param_verify/flask_example.py;line: 344">text_response_route</abbr>|    |
- Path: /api/text-resp
- Method: GET
- Request:
- Response:

    - TextRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|text/plain|text response|
        - Header
            {'X-Example-Type': 'text'}

### Name: html_response_route



**Desc**:test return html response

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:example/param_verify/flask_example.py;line: 353">html_response_route</abbr>|    |
- Path: /api/html-resp
- Method: GET
- Request:
- Response:

    - HtmlRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|text/html|html response|
        - Header
            {'X-Example-Type': 'html'}

### Name: file_response_route



**Desc**:test return file response

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:example/param_verify/flask_example.py;line: 362">file_response_route</abbr>|    |
- Path: /api/file-resp
- Method: GET
- Request:
- Response:

    - FileRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/octet-stream|file response|
        - Header
            {'X-Example-Type': 'file'}

</details><details><summary>Group: links</summary>

### Name: login_route

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:example/param_verify/flask_example.py;line: 375">login_route</abbr>|    |
- Path: /api/login
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |password|string|**`Required`**| |password||
        |uid|string|**`Required`**| |user id||
- Response:

    - LoginRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|login response|
        - Response Data

            |param name|type|default value|example|description|other|
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

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:example/param_verify/flask_example.py;line: 384">get_user_route</abbr>|    |
- Path: /api/user
- Method: GET
- Request:
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |token|string| | |token||
- Response:

    - SuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

### Name: pre_depend_contextmanager_route

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 277">pre_depend_contextmanager_route</abbr>|    |
- Path: /api/pre-depend-contextmanager
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- Response:

    - SuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 270">depend_contextmanager_route</abbr>|    |
- Path: /api/depend-contextmanager
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- Response:

    - SuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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



**Desc**:Test different request types, but they have the same alias and different parameter names

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 111">same_alias_route</abbr>|    |
- Path: /api/same-alias
- Method: GET
- Request:
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |token|string| | | ||
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |token|string| | | ||
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 264">pait_model_route</abbr>|    |
- Path: /api/pait-model
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |user_info|object|**`Required`**| | |[`properties:{'user_name': {'title': 'User Name', 'description': 'user name', 'maxLength': 4, 'minLength': 2, 'type': 'string'}, 'age': {'title': 'Age', 'description': 'age', 'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'type': 'integer'}}`], [`required:['user_name', 'age']`]|
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |user-agent|string|**`Required`**| |user agent||
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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


### Name: ~~raise_tip_route~~



**Desc**:test pait raise tip

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#DC143C>abandoned</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 65">raise_tip_route</abbr>|    |
- Path: /api/raise-tip
- Method: POST
- Request:
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |content__type|string|**`Required`**| |Content-Type||
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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


### Name: depend_route



**Desc**:Testing depend and using request parameters

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 97">depend_route</abbr>|    |
- Path: /api/depend
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |user-agent|string|**`Required`**| |user agent||
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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


</details><details><summary>Group: pait_doc</summary>

### Name: api doc.openapi_route

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:example;line: 65">add_doc_route.<locals>.openapi_route</abbr>|    |
- Path: /openapi.json
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- Response:


### Name: api doc.get_swagger_ui_html

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:example;line: 61">add_doc_route.<locals>.get_swagger_ui_html</abbr>|    |
- Path: /swagger
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- Response:


### Name: api doc.get_redoc_html

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:example;line: 57">add_doc_route.<locals>.get_redoc_html</abbr>|    |
- Path: /redoc
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- Response:


</details><details><summary>Group: plugin</summary>

### Name: check_json_plugin_route1



**Desc**:Test json plugin by resp type is typed dict

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:example/param_verify/flask_example.py;line: 433">check_json_plugin_route1</abbr>|    |
- Path: /api/check-json-plugin-1
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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


### Name: check_json_plugin_route



**Desc**:Test json plugin by resp type is dict

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:example/param_verify/flask_example.py;line: 392">check_json_plugin_route</abbr>|    |
- Path: /api/check-json-plugin
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

### Name: field_default_factory_route

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 123">field_default_factory_route</abbr>|    |
- Path: /api/field-default-factory
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |data_dict|object|**`Required`**| |test default factory||
        |data_list|array|**`Required`**| |test default factory|[`items:{'type': 'string'}`]|
        |demo_value|integer|**`Required`**| |Json body value not empty||
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 175">check_param_route</abbr>|    |
- Path: /api/check-param
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 208">check_response_route</abbr>|    |
- Path: /api/check-resp
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 78">post_route</abbr>|    |
- Path: /api/post
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**|123|user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**|so1n|user name|[`maxLength:4`], [`minLength:2`]|
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| |Content-Type||
- Response:

    - UserSuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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


### Name: test_cbv.get



**Desc**:Text cbv route get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 292">CbvRoute.get</abbr>|    |
- Path: /api/cbv
- Method: get
- Request:
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| | ||
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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


### Name: test_cbv.post



**Desc**:test cbv post method

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 317">CbvRoute.post</abbr>|    |
- Path: /api/cbv
- Method: post
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| | ||
- Response:

    - UserSuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 136">pait_base_field_route</abbr>|    |
- Path: /api/pait-base-field/<age>
- Method: POST
- Request:
    - Cookie Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |cookie|object|**`Required`**| |cookie||
    - File Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |upload_file|PydanticUndefined|**`Required`**| |upload file||
    - Form Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |a|string|**`Required`**| |form data||
        |b|string|**`Required`**| |form data||
    - Multiform Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |c|array|**`Required`**| |form data|[`items:{'type': 'string'}`]|
    - Multiquery Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |multi_user_name|array|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 4}`]|
    - Path Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |email|string|example@xxx.com| |user email||
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:example/param_verify/flask_example.py;line: 235">mock_route</abbr>|    |
- Path: /api/mock/<age>
- Method: GET
- Request:
    - Multiquery Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |multi_user_name|array|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 4}`]|
    - Path Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |email|string|example@xxx.com| |user email||
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`Required`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`Required`**| |user name|[`maxLength:4`], [`minLength:2`]|
- Response:

    - UserSuccessRespModel2

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
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

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
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
