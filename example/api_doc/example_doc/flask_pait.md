# Pait Doc
<details><summary>Group: root</summary>

### Name: test_raise_tip

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#DC143C>abandoned</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/flask_example.py;line: 27">test_raise_tip</abbr>|test pait raise tip|
- Path: /api/raise_tip
- Method: OPTIONS,POST
- Request:
    - Body

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |content__type|string|**`Required`**|Content-Type|{}|
- Response:


### Name: test_model

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/flask_example.py;line: 91">test_model</abbr>|Test Field|
- Path: /api/pait_model
- Method: HEAD,OPTIONS,GET
- Request:
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent|{}|
    - Query

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
- Response:


</details><details><summary>Group: user</summary>

### Name: test_post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/flask_example.py;line: 41">test_post</abbr>|Test Method:Post Pydantic Model|
- Path: /api/post
- Method: OPTIONS,POST
- Request:
    - Body

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|Content-Type|{}|
- Response:


### Name: demo_get2test_depend

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/flask_example.py;line: 55">demo_get2test_depend</abbr>|Test Method:Post request, Pydantic Model|
- Path: /api/depend
- Method: HEAD,OPTIONS,GET
- Request:
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent|{}|
    - Query

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
- Response:


### Name: test_pait

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/flask_example.py;line: 72">test_pait</abbr>|Test Field|
- Path: /api/get/<age>
- Method: HEAD,OPTIONS,GET
- Request:
    - Path

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|string|**`Required`**|None|{}|
    - Query

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |sex|enum|Only choose from: `man`,`woman`|None|{'enum': ['man', 'woman']}|
- Response:


### Name: test_cbv.get

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/flask_example.py;line: 101">TestCbv.get</abbr>|Text Pydantic Model and Field|
- Path: /api/cbv
- Method: get
- Request:
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|ua|{}|
    - Query

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |email|string|example@xxx.com|email|{}|
- Response:


### Name: test_cbv.post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/flask_example.py;line: 118">TestCbv.post</abbr>|test cbv post method|
- Path: /api/cbv
- Method: post
- Request:
    - Body

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|ua|{}|
- Response:


</details>