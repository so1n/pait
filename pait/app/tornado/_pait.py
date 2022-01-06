from typing import Any, Type

import aiofiles  # type: ignore
from tornado.web import RequestHandler

from pait.app.base import BaseAppHelper
from pait.core import Pait as _Pait
from pait.g import config
from pait.model import response

from ._app_helper import AppHelper

__all__ = ["pait", "Pait"]


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


class Pait(_Pait):
    app_helper_class: "Type[BaseAppHelper]" = AppHelper
    # If you assign a value directly, it will become a bound function
    make_mock_response_fn: staticmethod = staticmethod(make_mock_response)


pait = Pait()
