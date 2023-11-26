OpenAPI provides support for basic HTTP authentication through `security`, but different web frameworks implement basic HTTP authentication in different ways.
So `Pait` provides simple support for OpenAPI's security through `Depends` (`api key`, `http`, `oauth2`), which simplifies the use of security in different web frameworks.

!!! note

    advanced authentication such as jwt will be supported through other package in the future.

## 1.APIKey
`API Key` is the simplest method in Security, and because of its simplicity, it has the most usage scenarios.
`Pait` provides `APIKey` class to support the use of `API Key`, the usage is as follows:

=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/security/flask_with_apikey_demo.py" hl_lines="8-25 28-40"

    --8<-- "docs_source_code/openapi/security/flask_with_apikey_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/security/starlette_with_apikey_demo.py" hl_lines="10-27 30-42"
    --8<-- "docs_source_code/openapi/security/starlette_with_apikey_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/security/sanic_with_apikey_demo.py" hl_lines="8-25 28-40"
    --8<-- "docs_source_code/openapi/security/sanic_with_apikey_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/security/tornado_with_apikey_demo.py" hl_lines="9-26 29-44"
    --8<-- "docs_source_code/openapi/security/tornado_with_apikey_demo.py"
    ```

The first highlighting code is initialized for the different `APIKey` fields,
which use slightly different parameters, see the table below for parameter meanings:

| Parameters              | Description                                                                                                                                                                                                                        |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| name                    | The name of the `APIKey` field                                                                                                                                                                                                     |
| field                   | The `APIKey` field corresponds to the Field class in `Pait`, `API Key` only supports Query, Header and Cookie parameters, so only `field.Query`, `field.Header`, `field.Cookie` are allowed                                        |
| verify_api_key_callable | A function that checks `APIKey`, `Pait` extracts the `APIKey` value from the request body and passes it to the function for processing, if the function returns `True` then the check passes, and vice versa then the check fails. |
| security_name           | Specify the name of the security, the name of `APIKey` must be different for different roles, the default value is the class name of APIKey.                                                                                       |


!!! note

    In order to use APIKey properly in the OpenAPI tool, the `Field` must be initialized with the `openapi_include` attribute False.


The second highlighted piece of code connects APIKey to the route function via `Depend`,
where the argument to `Depend` is an instance of `APIKey`.
When the route function receives a request `Pait` automatically extracts the value of `APIKey` from the request body and passes it to `APIKey`'s `verify_api_key_callable` function for verification,
if it passes the verification the value is injected into the route function for execution,
and vice versa `401` is returned.

After running the code, execute the following command to see the execution effect of `APIKey`:
```bash
# Success Result
➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-cookie-key' \
  -H 'accept: */*' \
  -H 'Cookie: token=token'
{"code":0,"msg":"","data":"token"}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-header-key' \
  -H 'accept: */*' \
  -H 'token: token'
{"code":0,"msg":"","data":"token"}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-query-key?token=token' \
  -H 'accept: */*'
{"code":0,"msg":"","data":"token"}

# Fail Result
➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-cookie-key' \
  -H 'accept: */*' \
  -H 'Cookie: token='
Not authenticated

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-header-key' \
  -H 'accept: */*' \
  -H 'token: '
Not authenticated

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-query-key?token=' \
  -H 'accept: */*'
Not authenticated
```

### 1.1.Combination of APIKey and Links
Most of the parameters (e.g., Token) needed by route functions that use APIKey are obtained through other route functions.
In this case, you can describe the relationship between this route function and other route functions by using `Links` in `Field`,
such as the following scenario, which gets its Token from the login route function:

=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/security/flask_with_apikey_and_link_demo.py" hl_lines="15-33 38"

    --8<-- "docs_source_code/openapi/security/flask_with_apikey_and_link_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/security/starlette_with_apikey_and_link_demo.py" hl_lines="17-39 44"
    --8<-- "docs_source_code/openapi/security/starlette_with_apikey_and_link_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/security/sanic_with_apikey_and_link_demo.py" hl_lines="15-35 40"
    --8<-- "docs_source_code/openapi/security/sanic_with_apikey_and_link_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/security/tornado_with_apikey_and_link_demo.py" hl_lines="16-39 44"
    --8<-- "docs_source_code/openapi/security/tornado_with_apikey_and_link_demo.py"
    ```

The first highlighted code is from [Field-Links](/3_1_openapi/#41links), while the `Query` in the second highlighted code sets the `links` attribute to `link_login_token_model`.
This way `Pait` will bind `login_route` to `api_key_query_route` via Link when generating OpenAPI.

!!! note
    `openapi_include=False` causes `Swggaer` to be unable to display Link data.


## 2.HTTP
There are two types of HTTP basic authentication, one is `HTTPBasic` and the other is `HTTPBearer` or `HTTPDIgest`.
The difference between the two is that `HTTPBasic` needs to verify the `username` and `password` parameters in the request header,
and if the verification is successful, it means the authentication is successful.
If the validation error will return `401` response, the browser will pop up a window to let the user enter `username` and `password`.
While `HTTPBearer` or `HTTPDIgest` only need to pass `token` in the request header as required.


`Pait` encapsulates the `HTTPBasic`, `HTTPBearer` and `HTTPDigest` classes for each of the three methods of HTTP basic authentication.
Like `APIKey` they need to be bound to a route function via `Depend`, which is used as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/security/flask_with_http_demo.py"

    --8<-- "docs_source_code/openapi/security/flask_with_http_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/security/starlette_with_http_demo.py"
    --8<-- "docs_source_code/openapi/security/starlette_with_http_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/security/sanic_with_http_demo.py"
    --8<-- "docs_source_code/openapi/security/sanic_with_http_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/security/tornado_with_http_demo.py"
    --8<-- "docs_source_code/openapi/security/tornado_with_http_demo.py"
    ```

You can see that the whole code consists of two parts, the first part initializes the corresponding basic authentication class,
and the second part uses `Depend` in the route function to get an instance of the authentication class.

However, `HTTPBasic` is used a little differently than the other two,
for example, `HTTPBasic` has different initialization parameters than the other two, which are described in the following table:

|parameter|description|
|---|---|
|security_model|OpenAPI Description Model about HTTPBasic, a generic HTTPBasicModel has been provided by default, for customization needs visit OpenAPI's [securitySchemeObject](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#securitySchemeObject)|
|security_name|Specifies the name of the Security, the name of the basic authentication instance must be different for different roles, the default value is class name. |
|header_field|Instance of Header Field for `Pait` |
|realm|The realm parameter of HTTP basic authentication  |

While `HTTPBearer` and `HTTPDigest` are used in a similar way as `APIKey`,
they need to be initialized as required and bound to the route function via `Depend`,
their parameters are described as follows:

|parameter| description                                                                                                                                                                                                                                                    |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|security_model| OpenAPI Description Model about HTTPBasic, a generic HTTPBasicModel has been provided by default, for customization needs visit OpenAPI's [securitySchemeObject](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#securitySchemeObject) |
|security_name| Specifies the name of the Security, the name of the basic authentication instance must be different for different roles, the default value is class name.                                                                                               |
|header_field| Instance of Header Field for `Pait`                                                                                                                                                                                                                            |
|is_raise| When set to `True`, `Pait` throws a standard error if parsing fails, and `False` returns `None` if parsing fails, default `True`.                                                                                                                              |
| verify_callable | Accepts a checksum function, `Pait` extracts the value from the request body and passes it to the checksum function, if it returns `True` it means the checksum passes, otherwise the checksum fails.                                                                                                                                                                                            |

In addition to the difference in initialization parameters,
`HTTPBasic` is not used directly in the route function,
but exists in the `get_user_name` function and the `get_user_name` function is responsible for authentication.
returning the username to the route function if the authentication is successful, otherwise returning a `401` response.



After running the code, execute the `curl` command to see them executed as follows:
```bash
# Success Result
➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-basic-credentials' \
  -H 'accept: */*' \
  -H 'Authorization: Basic c28xbjpzbzFu'

{"code":0,"data":"so1n","msg":""}

➜   curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-bearer' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer http'

{"code":0,"data":"http","msg":""}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-digest' \
  -H 'accept: */*' \
  -H 'Authorization: Digest http'

{"code":0,"data":"http","msg":""}

# Fail Result
➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-digest' \
  -H 'accept: */*' \
  -H 'Authorization: Digest '

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>403 Forbidden</title>
<h1>Forbidden</h1>
<p>Not authenticated</p>

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-bearer' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer '

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>403 Forbidden</title>
<h1>Forbidden</h1>
<p>Not authenticated</p>
```

!!! note

    The `HTTPDigest` class only provides simple `HTTPDigest` authentication support,
    which needs to be modified to suit your business logic when using it.

## 3.Oauth2
OAuth 2.0 is an authorization protocol that provides API clients with limited access to user data on the Web server.
In addition to providing identity verification, it also supports privilege verification, which is used as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/security/flask_with_oauth2_demo.py"

    --8<-- "docs_source_code/openapi/security/flask_with_oauth2_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/security/starlette_with_oauth2_demo.py"
    --8<-- "docs_source_code/openapi/security/starlette_with_oauth2_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/security/sanic_with_oauth2_demo.py"
    --8<-- "docs_source_code/openapi/security/sanic_with_oauth2_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/security/tornado_with_oauth2_demo.py"
    --8<-- "docs_source_code/openapi/security/tornado_with_oauth2_demo.py"
    ```

The first part is to create a Model -- `User`  about the user's data and a `temp_token_dict` with `key` as token `value` as `User` to be used to mocker database storage.

The second part is to create a standard login route function that takes a parameter of type `OAuth2PasswordRequestFrom`,
which is `Pait`'s encapsulation of `Oauth2`'s login parameters, and which has the following source code:
```Python
from pydantic import BaseModel
from pait.field import Form

class BaseOAuth2PasswordRequestFrom(BaseModel):
    username: str = Form()
    password: str = Form()
    scope: ScopeType = Form("")
    client_id: Optional[str] = Form(None)
    client_secret: Optional[str] = Form(None)


class OAuth2PasswordRequestFrom(BaseOAuth2PasswordRequestFrom):
    grant_type: Optional[str] = Form(None, regex="password")
```
can see that `OAuth2PasswordRequestFrom` inherits `BaseModel` and uses `Form` for the `Field` of all its parameters,
which means that its parameters get data from the form in the request body.
While the login route function simply checks the data after receiving it,
and returns a 400 response if the check is wrong.
If it passes, it generates a `token` and stores the `token` and `User` in `temp_token_dict` and returns the Oauth2 standard response via `oauth2.OAuth2PasswordBearerJsonRespModel`.

The third part is the creation of an instance of `oauth2_pb` via `oauth2.OAuth2PasswordBearer` as well as the creation of a function  -- `get-current_user`to get the user.
The `scopes` parameter to create `oauth2_pb` is the permission description of `oauth2_pb` and the `route` parameter is the login route function,
when the route function registers with the web framework, `oauth2_pb` will find the URL of the route function and writes it to the `tokenUrl` attribute.
The `get_current_user` function will get the current user through the Token, and then through the `is_allow` method to determine whether the current user has permission to access the route function,
if not, then return a 403 response, if so, then return `User` Model.
Note that the `get_current_user` function receives the value of the `oauth2.OAuth2PasswordBearer` proxy class,
which already specifies only which permissions are allowed(by `oauth2_pb.get_depend` method).
In addition, the class has two functions, one that passes the requested parameters to the function via `Depend`,
and the other that provides the `is_allow` method for determining whether the user has permission to access the interface.

The fourth part is the route functions, which use the `get_current_user` function created in the third part.
where `oauth2_pb.get_depend(["user-name"])` creates an instance of a proxy that only allows access with `user-name` privileges, via `oauth2.OAuth2PasswordBearer`.
`oauth2_pb.get_depend(["user-info"])` will create a proxy instance that only allows access with `user-info` permissions via `oauth2.OAuth2PasswordBearer`.
The only difference between them is that the `scopes` are different.

After running the code, run the `curl` command to see them executed as follows:
```bash
➜  curl 'http://127.0.0.1:8000/api/oauth2-login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw 'grant_type=password&scope=user-info&username=so1n&password=so1n' \

{"access_token":"pomeG4jCDh","token_type":"bearer"}

➜  curl 'http://127.0.0.1:8000/api/oauth2-login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw 'grant_type=password&scope=user-name&username=so1n1&password=so1n1' \

{"access_token":"G8ckqKGkDO","token_type":"bearer"}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/oauth2-user-info' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer pomeG4jCDh'

{"code":0,"data":{"age":23,"name":"so1n","scopes":["user-info"],"sex":"M","uid":"123"},"msg":""}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/oauth2-user-info' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer G8ckqKGkDO'

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Not authenticated</p>

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/oauth2-user-name' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer pomeG4jCDh'

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Not authenticated</p>

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/oauth2-user-name' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer G8ckqKGkDO'
{"code":0,"data":"so1n1","msg":""}

```
The response result shows that a user with permission `user-info` can only access `/api/oauth2-user-info`,
while a user with permission `user-name` can only access `/api/oauth2-user-name`.

!!! note

    The current version does not support `refresh Url` yet
