import json
from typing import Any, Dict, Optional

from pydantic.fields import Undefined

from .base_parse import PaitBaseParse


class NormalEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is Undefined:
            return 'Required'
        else:
            return json.JSONEncoder.default(self, obj)


def dumps(obj, **kwargs):
    return json.dumps(obj, cls=NormalEncoder, **kwargs)


def loads(json_str, **kwargs):
    return json.loads(json_str, **kwargs)


class PaitJson(PaitBaseParse):
    def __init__(self, title: str = 'Pait Json', filename: Optional[str] = None, indent: Optional[int] = None):
        super().__init__()

        pait_dict: Dict[str, Any] = self.gen_dict()
        pait_dict['title'] = title

        pait_json: str = dumps(pait_dict, indent=indent)
        self.output_file(filename, pait_json, '.json')
