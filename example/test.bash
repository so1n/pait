#!/bin/sh

echo $(curl -s "127.0.0.1:8000/api/3?uid=123&user_name=appl&sex=man")
echo $(curl -s "127.0.0.1:8000/api1?uid=123&user_name=appl&age=2")
echo $(curl -s -H "Content-Type:application/json" -H "Data_Type:msg" -X POST --data '{"uid":123,"user_name":"appl","age":2}' 127.0.0.1:8000/api)
echo $(curl -s -H "Content-Type:application/json" -H "Data_Type:msg" -X POST --data '{"uid":123,"user_name":"appl","age":2}' 127.0.0.1:8000/api1)
