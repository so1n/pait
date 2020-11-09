#!/bin/sh

echo $(curl -s "127.0.0.1:8000/api/get/3?uid=123&user_name=appl&sex=man")
echo $(curl -s "127.0.0.1:8000/api/depend?uid=123&user_name=appl&age=2")
echo $(curl -s "127.0.0.1:8000/api/cbv?uid=123&user_name=appl&age=2")
echo $(curl -s "127.0.0.1:8000/api/pait_model?uid=123&user_name=appl")
echo $(curl -s -H "Content-Type:application/json" -H "Data_Type:msg" -X POST --data '{"uid":123,"user_name":"appl","age":2}' 127.0.0.1:8000/api/cbv)
echo $(curl -s -H "Content-Type:application/json" -H "Data_Type:msg" -X POST --data '{"uid":123,"user_name":"appl","age":2}' 127.0.0.1:8000/api/post)
echo $(curl -s -H "Content-Type:application/json" -H "Data_Type:msg" -X POST --data '{"uid":123,"user_name":"appl","age":2}' 127.0.0.1:8000/api/raise_tip)
