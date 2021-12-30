import json
from typing import Any, AsyncContextManager, Callable, Dict, List, Optional, Tuple, Type

import aiofiles  # type: ignore
from pydantic import BaseConfig
from sanic import response as sanic_response
from sanic.response import json as resp_json
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.core import pait as _pait
from pait.g import config
from pait.model import response
from pait.model.status import PaitStatus

from ._app_helper import AppHelper

__all__ = ["pait"]


async def make_mock_response(pait_response: Type[response.PaitBaseResponseModel]) -> sanic_response.BaseHTTPResponse:
    if issubclass(pait_response, response.PaitJsonResponseModel):
        resp: sanic_response.BaseHTTPResponse = resp_json(
            json.loads(pait_response.get_example_value(json_encoder_cls=config.json_encoder))
        )
    elif issubclass(pait_response, response.PaitTextResponseModel) or issubclass(
        pait_response, response.PaitHtmlResponseModel
    ):
        resp = sanic_response.text(pait_response.get_example_value(), content_type=pait_response.media_type)
    elif issubclass(pait_response, response.PaitFileResponseModel):
        named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
        f: Any = await named_temporary_file.__aenter__()
        await f.write(pait_response.get_example_value())
        await f.seek(0)
        resp = await sanic_response.file_stream(f.name, mime_type=pait_response.media_type)

        raw_streaming_fn = resp.streaming_fn

        async def _streaming_fn(_response: sanic_response.BaseHTTPResponse) -> None:
            await raw_streaming_fn(_response)
            await named_temporary_file.__aexit__(None, None, None)

        resp.streaming_fn = _streaming_fn
    else:
        raise NotImplementedError(f"make_mock_response not support {pait_response}")
    resp.status = pait_response.status_code[0]
    if pait_response.header:
        resp.headers.update(pait_response.header)
    return resp


def pait(
    # param check
    at_most_one_of_list: Optional[List[List[str]]] = None,
    required_by: Optional[Dict[str, List[str]]] = None,
    pre_depend_list: Optional[List[Callable]] = None,
    make_mock_response_fn: Optional[Callable[[Type[response.PaitBaseResponseModel]], Any]] = None,
    # doc
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
    tag: Optional[Tuple[str, ...]] = None,
    enable_mock_response: bool = False,
    response_model_list: Optional[List[Type[response.PaitBaseResponseModel]]] = None,
    pydantic_model_config: Optional[Type[BaseConfig]] = None,
) -> Callable:
    """Help starlette provide parameter checks and type conversions for each routing function/cbv class"""
    return _pait(
        AppHelper,
        make_mock_response_fn=make_mock_response_fn or make_mock_response,
        author=author,
        desc=desc,
        summary=summary,
        name=name,
        status=status,
        group=group,
        tag=tag,
        enable_mock_response=enable_mock_response,
        response_model_list=response_model_list,
        pre_depend_list=pre_depend_list,
        at_most_one_of_list=at_most_one_of_list,
        required_by=required_by,
        pydantic_model_config=pydantic_model_config,
    )
