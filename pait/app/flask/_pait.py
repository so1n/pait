import json
from tempfile import NamedTemporaryFile
from typing import Type

from flask import Response, jsonify, make_response, send_from_directory

from pait.app.base.app_helper import BaseAppHelper
from pait.core import Pait as _Pait
from pait.g import config
from pait.model import response

from ._app_helper import AppHelper

__all__ = ["pait", "Pait"]


def make_mock_response(pait_response: Type[response.PaitBaseResponseModel]) -> Response:
    if issubclass(pait_response, response.PaitJsonResponseModel):
        resp: Response = jsonify(json.loads(pait_response.get_example_value(json_encoder_cls=config.json_encoder)))
    elif issubclass(pait_response, response.PaitTextResponseModel) or issubclass(
        pait_response, response.PaitHtmlResponseModel
    ):
        resp = make_response(pait_response.get_example_value())
        resp.mimetype = pait_response.media_type
    elif issubclass(pait_response, response.PaitFileResponseModel):
        with NamedTemporaryFile(delete=True) as temporary_file:
            temporary_file.write(pait_response.get_example_value())
            temporary_file.seek(0)
            _, f_path, f_filename = temporary_file.name.split("/")
            resp = send_from_directory("/" + f_path, f_filename, mimetype=pait_response.media_type)
    else:
        raise NotImplementedError(f"make_mock_response not support {pait_response}")
    resp.status_code = pait_response.status_code[0]
    if pait_response.header:
        resp.headers.update(pait_response.header)  # type: ignore
    return resp


class Pait(_Pait):
    app_helper_class: "Type[BaseAppHelper]" = AppHelper
    # If you assign a value directly, it will become a bound function
    make_mock_response_fn: staticmethod = staticmethod(make_mock_response)
    # make_mock_response_fn: Callable[[Type[response.PaitBaseResponseModel]], Any] = staticmethod(make_mock_response)


pait = Pait()
