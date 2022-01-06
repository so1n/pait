# Pait Doc
<details><summary>Group: check_resp</summary>

### Name: text_response_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 355">text_response_route</abbr>||
- Path: /api/text-resp
- Method: GET,HEAD
- Request:
- Response:

    - TextRespModel

        |status code|media type|description|
        |---|---|---|
        |200|text/plain|text response|
        - Header
            {'X-Example-Type': 'text'}

### Name: html_response_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 363">html_response_route</abbr>||
- Path: /api/html-resp
- Method: GET,HEAD
- Request:
- Response:

    - HtmlRespModel

        |status code|media type|description|
        |---|---|---|
        |200|text/html|html response|
        - Header
            {'X-Example-Type': 'html'}

### Name: file_response_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 371">file_response_route</abbr>||
- Path: /api/file-resp
- Method: GET,HEAD
- Request:
- Response:

    - FileRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/octet-stream|file response|
        - Header
            {'X-Example-Type': 'file'}

</details><details><summary>Group: links</summary>

### Name: login_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 388">login_route</abbr>||
- Path: /api/login
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |password|string|**`Required`**|password||
        |uid|string|**`Required`**|user id||
- Response:

    - LoginRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|login response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.token|string|**`Required`**|||
            |msg|string|success|api status msg||
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

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 401">get_user_route</abbr>||
- Path: /api/user
- Method: GET,HEAD
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |token|string||token||
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


</details><details><summary>Group: other</summary>

### Name: raise_tip_route



**Desc**:test pait raise tip

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#DC143C>abandoned</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 58">raise_tip_route</abbr>||
- Path: /api/raise-tip
- Method: POST
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |content__type|string|**`Required`**|Content-Type||
- Response:

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
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


### Name: post_route



**Desc**:Test Method:Post Pydantic Model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 71">post_route</abbr>||
- Path: /api/post
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 25}|
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000, 'example': '123'}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'example': 'so1n'}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|Content-Type||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
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
                "content_type": ""
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


### Name: pait_model_route



**Desc**:Test pait model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 248">pait_model_route</abbr>||
- Path: /api/pait-model
- Method: POST
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user_info|object|**`Required`**|None|{'properties': {'user_name': {'title': 'User Name', 'description': 'user name', 'maxLength': 4, 'minLength': 2, 'type': 'string'}, 'age': {'title': 'Age', 'description': 'age', 'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'type': 'integer'}}, 'required': ['user_name', 'age']}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
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


### Name: depend_contextmanager_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 254">depend_contextmanager_route</abbr>||
- Path: /api/check_depend_contextmanager
- Method: GET,HEAD
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


### Name: depend_async_contextmanager_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 287">depend_async_contextmanager_route</abbr>||
- Path: /api/check_depend_async_contextmanager
- Method: GET,HEAD
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


### Name: pre_depend_contextmanager_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 263">pre_depend_contextmanager_route</abbr>||
- Path: /api/check_pre_depend_contextmanager
- Method: GET,HEAD
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


### Name: pre_depend_async_contextmanager_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 275">pre_depend_async_contextmanager_route</abbr>||
- Path: /api/check_pre_depend_async_contextmanager
- Method: GET,HEAD
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


</details><details><summary>Group: user</summary>

### Name: depend_route



**Desc**:Test Method:Post request, Pydantic Model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 90">depend_route</abbr>||
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
- Response:

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
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


### Name: pait_base_field_route



**Desc**:Test the use of all BaseField-based

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 115">pait_base_field_route</abbr>||
- Path: /api/pait-base-field/{age}
- Method: GET,HEAD
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

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
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


### Name: same_alias_route

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 104">same_alias_route</abbr>||
- Path: /api/same-alias
- Method: GET,HEAD
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

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
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


### Name: mock_route



**Desc**:Test gen mock response

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 217">mock_route</abbr>||
- Path: /api/mock/{age}
- Method: GET,HEAD
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


### Name: CbvRoute.get



**Desc**:Text cbv route get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 299">CbvRoute.get</abbr>||
- Path: /api/cbv
- Method: get
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|None||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 25}|
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
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
                "content_type": ""
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


### Name: CbvRoute.post



**Desc**:test cbv post method

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 326">CbvRoute.post</abbr>||
- Path: /api/cbv
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 25}|
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|None||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
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
                "content_type": ""
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


### Name: check_param_route



**Desc**:Test check param

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 156">check_param_route</abbr>||
- Path: /api/check-param
- Method: GET,HEAD
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


### Name: check_response_route



**Desc**:Test test-helper check response

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 189">check_response_route</abbr>||
- Path: /api/check-resp
- Method: GET,HEAD
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


</details>
