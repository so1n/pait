from typing import Any, Callable, Dict, List, Optional, Tuple, Type

import aiofiles  # type: ignore
from pydantic import BaseConfig
from tornado.web import RequestHandler

from pait.core import pait as _pait
from pait.g import config
from pait.model import response
from pait.model.status import PaitStatus

from ._app_helper import AppHelper

__all__ = ["pait"]


async def make_mock_response(pait_response: Type[response.PaitBaseResponseModel]) -> Any:
    tornado_handle: RequestHandler = getattr(pait_response, "handle", None)
    if not tornado_handle:
        raise RuntimeError("Can not load Tornado handle")
    tornado_handle.set_status(pait_response.status_code[0])
    for key, value in pait_response.header.items():
        tornado_handle.set_header(key, value)
    tornado_handle.set_header("Content-Type", pait_response.media_type)
    if issubclass(pait_response, response.PaitJsonResponseModel):
        tornado_handle.write(pait_response.get_example_value(json_encoder_cls=config.json_encoder))
    elif issubclass(pait_response, response.PaitTextResponseModel) or issubclass(
        pait_response, response.PaitHtmlResponseModel
    ):
        tornado_handle.write(pait_response.get_example_value())
    elif issubclass(pait_response, response.PaitFileResponseModel):
        async with aiofiles.tempfile.NamedTemporaryFile() as f:  # type: ignore
            await f.write(pait_response.get_example_value())
            await f.seek(0)
            async for line in f:
                tornado_handle.write(line)
    else:
        raise NotImplementedError()


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
