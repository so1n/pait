# AnyApi
### Name: demo.demo
**Tag**: default
- Path: /api/demo
- Method: get
- Request:
    **query**

     |Name|Default|Type|Desc|Example|Other|
     |---|---|---|---|---|---|
     |uid|`Required`|integer|user id||exclusiveMinimum:10;<br>exclusiveMaximum:1000|
     |age|`Required`|integer|age||exclusiveMinimum:0|
     |username|`Required`|string|user name||maxLength:4;<br>minLength:2|


- Response
**Desc**: demo json response
*Header*

    - 200:application/json; charset=utf-8
    **Response Info**

         |Name|Default|Type|Desc|Example|Other|
         |---|---|---|---|---|---|
         |code|`Required`|integer|||minimum:0|
         |msg|`Required`|string||||
         |data|`Required`|array|||items:{'$ref': '#/components/schemas/UserModel'}|

        **Response Example**

        ```json
        {
            "code": 0,
            "msg": "",
            "data": {
                "name": "so1n",
                "uid": 0,
                "age": 0
            }
        }
        ```
**Desc**: demo json response
*Header*

    - 201:application/json; charset=utf-8
    **Response Info**

         |Name|Default|Type|Desc|Example|Other|
         |---|---|---|---|---|---|
         |code|`Required`|integer|||minimum:0|
         |msg|`Required`|string||||
         |data|`Required`|array|||items:{'$ref': '#/components/schemas/UserModel'}|

        **Response Example**

        ```json
        {
            "code": 0,
            "msg": "",
            "data": {
                "name": "so1n",
                "uid": 0,
                "age": 0
            }
        }
        ```
**Desc**: demo json response
*Header*

    - 404:application/json; charset=utf-8
    **Response Info**

         |Name|Default|Type|Desc|Example|Other|
         |---|---|---|---|---|---|
         |code|`Required`|integer|||minimum:0|
         |msg|`Required`|string||||
         |data|`Required`|array|||items:{'$ref': '#/components/schemas/UserModel'}|

        **Response Example**

        ```json
        {
            "code": 0,
            "msg": "",
            "data": {
                "name": "so1n",
                "uid": 0,
                "age": 0
            }
        }
        ```
