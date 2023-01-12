from typing import Any

from pait.g import config
from pait.param_handle import AsyncParamHandler, ParamHandler


class NotTipParamHandler(ParamHandler):
    tip_exception_class = None


class NotTipAsyncParamHandler(AsyncParamHandler):
    tip_exception_class = None


def my_serialization(content_dict: dict, **kwargs: Any) -> str:
    import json

    import yaml  # type: ignore

    return yaml.dump(json.loads(json.dumps(content_dict, cls=config.json_encoder), **kwargs))
