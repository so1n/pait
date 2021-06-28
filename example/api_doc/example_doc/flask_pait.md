# Pait Doc
<details><summary>Group: root</summary>

### Name: test_model



**Desc**:Test Field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:example/param_verify/flask_example.py;line: 145">test_model</abbr>||
- Path: /api/pait_model
- Method: POST,OPTIONS
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
            |data.uid|integer|6666666666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": [
                {
                  "uid": 6666666666,
                  "user_name": "mock_name",
                  "age": 99,
                  "content_type": "application/json"
                }
              ]
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
|so1n|<font color=#DC143C>abandoned</font>|<abbr title="file:example/param_verify/flask_example.py;line: 29">test_raise_tip</abbr>||
- Path: /api/raise_tip
- Method: POST,OPTIONS
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
            |data.uid|integer|6666666666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": [
                {
                  "uid": 6666666666,
                  "user_name": "mock_name",
                  "age": 99,
                  "content_type": "application/json"
                }
              ]
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

### Name: test_other_field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 88">test_other_field</abbr>||
- Path: /api/other_field
- Method: POST,OPTIONS
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


### Name: demo_get2test_depend



**Desc**:Test Method:Post request, Pydantic Model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 69">demo_get2test_depend</abbr>||
- Path: /api/depend
- Method: POST,OPTIONS
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
            |data.uid|integer|6666666666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": [
                {
                  "uid": 6666666666,
                  "user_name": "mock_name",
                  "age": 99,
                  "content_type": "application/json"
                }
              ]
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
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 48">test_post</abbr>||
- Path: /api/post
- Method: POST,OPTIONS
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
            |data.uid|integer|6666666666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": [
                {
                  "uid": 6666666666,
                  "user_name": "mock_name",
                  "age": 99,
                  "content_type": "application/json"
                }
              ]
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
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 156">TestCbv.get</abbr>||
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
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|example@so1n.me|user email||
            |data.uid|integer|6666666666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 6666666666,
                "user_name": "mock_name",
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


### Name: test_cbv.post



**Desc**:test cbv post method

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 174">TestCbv.post</abbr>||
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
            |data.uid|integer|6666666666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": [
                {
                  "uid": 6666666666,
                  "user_name": "mock_name",
                  "age": 99,
                  "content_type": "application/json"
                }
              ]
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
|so1n|<font color=#32CD32>release</font>|<abbr title="file:example/param_verify/flask_example.py;line: 115">test_pait</abbr>||
- Path: /api/get/<age>
- Method: OPTIONS,HEAD,GET
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
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|example@so1n.me|user email||
            |data.uid|integer|6666666666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 6666666666,
                "user_name": "mock_name",
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