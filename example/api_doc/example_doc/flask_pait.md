# Pait Doc
<details><summary>Group: root</summary>

### Name: test_pre_depend_contextmanager

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:example/param_verify/flask_example.py;line: 269">test_pre_depend_contextmanager</abbr>||
- Path: /api/check_pre_depend_contextmanager
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |is_raise|boolean|False|None||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_depend_contextmanager

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:example/param_verify/flask_example.py;line: 262">test_depend_contextmanager</abbr>||
- Path: /api/check_depend_contextmanager
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |is_raise|boolean|False|None||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_model



**Desc**:Test Field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:example/param_verify/flask_example.py;line: 254">test_model</abbr>||
- Path: /api/pait_model
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|application/json|content-type||
            |data.uid|integer|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success|api status msg||
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
                "content_type": "application/json"
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_raise_tip



**Desc**:test pait raise tip

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#DC143C>abandoned</font>|<abbr title="file:example/param_verify/flask_example.py;line: 33">test_raise_tip</abbr>||
- Path: /api/raise_tip
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |content__type|string|**`Required`**|Content-Type||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|application/json|content-type||
            |data.uid|integer|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success|api status msg||
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
                "content_type": "application/json"
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: api doc.openapi_route

|Author|Status|func|summary|
|---|---|---|---|
||undefined|<abbr title="file:example;line: 51">add_doc_route.<locals>.openapi_route</abbr>||
- Path: /openapi.json
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |pin_code|string||None||
- Response:


### Name: api doc.get_swagger_ui_html

|Author|Status|func|summary|
|---|---|---|---|
||undefined|<abbr title="file:example;line: 47">add_doc_route.<locals>.get_swagger_ui_html</abbr>||
- Path: /swagger
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |pin_code|string||None||
- Response:


### Name: api doc.get_redoc_html

|Author|Status|func|summary|
|---|---|---|---|
||undefined|<abbr title="file:example;line: 43">add_doc_route.<locals>.get_redoc_html</abbr>||
- Path: /redoc
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |pin_code|string||None||
- Response:


</details><details><summary>Group: user</summary>

### Name: test_other_field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 104">test_other_field</abbr>||
- Path: /api/other_field
- Method: POST
- Request:
    - Cookie Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |cookie|object|**`Required`**|cookie||
    - File Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |upload_file|PydanticUndefined|**`Required`**|upload file||
    - Form Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |a|string|**`Required`**|form data||
        |b|string|**`Required`**|form data||
    - Multiform Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |c|array|**`Required`**|form data|{'items': {'type': 'string'}}|
- Response:


### Name: test_check_param



**Desc**:Test check param

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 131">test_check_param</abbr>||
- Path: /api/check_param
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |alias_user_name|string|None|user name|{'maxLength': 4, 'minLength': 2}|
        |birthday|string|None|birthday||
        |email|string|example@xxx.com|user email||
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|None|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 99}|
            |data.email|string|**`Required`**|user email|{'example': 'example@so1n.me'}|
            |data.multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'example': ('mock_name',), 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000, 'example': 666}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 10, 'minLength': 2, 'example': 'mock_name'}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_same_alias

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 92">test_same_alias</abbr>||
- Path: /api/same_alias
- Method: GET
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |token|string||None||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |token|string||None||
- Response:


### Name: test_check_response



**Desc**:Test check param

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 164">test_check_response</abbr>||
- Path: /api/check_resp
- Method: GET
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |display_age|integer|0|display_age||
        |email|string|example@xxx.com|user email||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|None|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel3

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**|user email||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: demo_get2test_depend



**Desc**:Test Method:Post request, Pydantic Model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 73">demo_get2test_depend</abbr>||
- Path: /api/depend
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|application/json|content-type||
            |data.uid|integer|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success|api status msg||
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
                "content_type": "application/json"
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_post



**Desc**:Test Method:Post Pydantic Model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 52">test_post</abbr>||
- Path: /api/post
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|Content-Type||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|application/json|content-type||
            |data.uid|integer|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success|api status msg||
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
                "content_type": "application/json"
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_cbv.post



**Desc**:test cbv post method

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 303">TestCbv.post</abbr>||
- Path: /api/cbv
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|ua||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|application/json|content-type||
            |data.uid|integer|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success|api status msg||
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
                "content_type": "application/json"
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_cbv.get



**Desc**:Text Pydantic Model and Field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 285">TestCbv.get</abbr>||
- Path: /api/cbv
- Method: get
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|ua||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |email|string|example@xxx.com|email||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 99}|
            |data.email|string|**`Required`**|user email|{'example': 'example@so1n.me'}|
            |data.multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'example': ('mock_name',), 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000, 'example': 666}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 10, 'minLength': 2, 'example': 'mock_name'}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_mock



**Desc**:Test Field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 223">test_mock</abbr>||
- Path: /api/mock/<age>
- Method: GET
- Request:
    - Multiquery Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
    - Path Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |email|string|example@xxx.com|user email||
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 99}|
            |data.email|string|**`Required`**|user email|{'example': 'example@so1n.me'}|
            |data.multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'example': ('mock_name',), 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000, 'example': 666}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 10, 'minLength': 2, 'example': 'mock_name'}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: test_pait



**Desc**:Test Field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 193">test_pait</abbr>||
- Path: /api/get/<age>
- Method: GET
- Request:
    - Multiquery Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
    - Path Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |email|string|example@xxx.com|user email||
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 99}|
            |data.email|string|**`Required`**|user email|{'example': 'example@so1n.me'}|
            |data.multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'example': ('mock_name',), 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000, 'example': 666}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 10, 'minLength': 2, 'example': 'mock_name'}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details>
