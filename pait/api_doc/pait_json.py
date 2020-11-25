import json
from typing import Any, Dict, List, Optional
from types import CodeType

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
    def __init__(self, title: str = 'Pait Json', output_file: Optional[str] = None, indent: Optional[int] = None):
        super().__init__()

        pait_dict: Dict[str, Any] = self.gen_dict()
        pait_dict['title'] = title

        pait_json: str = dumps(pait_dict, indent=indent)

        if not output_file:
            print(pait_json)
        else:
            if not output_file.endswith('.json'):
                output_file += '.json'
            with open(output_file, mode='a') as f:
                f.write(pait_json)

    def gen_dict(self) -> Dict[str, Any]:
        api_doc_dict: Dict[str, Any] = {}
        for group in self._group_list:
            group_dict: Dict[str, Any] = api_doc_dict.setdefault(group, {})
            group_dict['name'] = group
            group_dict['group_list'] = []
            for pait_model in self._tag_pait_dict[group]:
                func_code: CodeType = pait_model.func.__code__
                response_list: List[Dict[str, Any]] = []
                if pait_model.response_model_list:
                    for resp_model_class in pait_model.response_model_list:
                        resp_model = resp_model_class()
                        response_list.append({
                            'status_code': ','.join([str(i) for i in resp_model.status_code]),
                            'media_type': resp_model.media_type,
                            'description': resp_model.description,
                            'header': resp_model.header,
                            'response_data': self._parse_schema(resp_model.response_data.schema())
                        })
                group_dict['group_list'].append({
                    'name': pait_model.operation_id,
                    'status': pait_model.status.value,
                    'author': ','.join(pait_model.author),
                    'func': {
                        'file': func_code.co_filename,
                        'lineno': func_code.co_firstlineno,
                        'name': pait_model.func.__qualname__
                    },
                    'path': pait_model.path,
                    'method': ','.join(pait_model.method_set),
                    'request': self._parse_func_param(pait_model.func),
                    'response_list': response_list
                })
        return api_doc_dict
