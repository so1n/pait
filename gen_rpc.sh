#!/bin/bash
# gen python protos code path
target_p='pait/http'
# project proto path
source_p='pait/http'

poetry run python -m grpc_tools.protoc \
  --mypy_grpc_out=./$source_p \
  --mypy_out=./$source_p \
  --python_out=./$source_p \
  --grpc_python_out=./$source_p \
  -I $source_p $(find ./$source_p -name '*.proto')
