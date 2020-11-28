import json
from typing import Any, Dict, Optional

from pydantic.fields import Undefined

from .base_parse import PaitBaseParse
from pait import field as pait_field


class PaitOpenApiJson(PaitBaseParse):
    def __init__(
            self,
            filename: Optional[str] = None,
            open_api_info: Optional[Dict[str, Any]] = None,
            open_api_server: Optional[Dict[str, Any]] = None
    ):
        super().__init__()
        if not open_api_info:
            open_api_info = {}
        if not open_api_server:
            open_api_server = {"url": "/"}
        self.open_api_dict = {
            "openapi": "3.0.0",
            "info": open_api_info,
            "servers": open_api_server,
            "tags": {
                "name": "test",
                "description": "about test api",
                "externalDocs": {
                    "description": "external docx",
                    "url": " http://example.com"
                }
            },
            "paths": {},
            "components": {"schema": {}},
            "security": {},
            "externalDocs": {}
        }
        self.parse_data_2_openapi()
        pait_json: str = json.dumps(self.open_api_dict)
        self.output_file(filename, pait_json, '.json')

    def change_ref(self, schema, path):
        for key, value in schema.items():
            if key == '$ref' and not value.startswith('#/components'):
                schema[key] = f"{path}{value[1:]}"
            if type(value) is dict:
                self.change_ref(value, path)

    def parse_data_2_openapi(self):
        for group, pait_model_list in self._tag_pait_dict.items():
            for pait_model in pait_model_list:
                path: str = pait_model.path
                path_dict: dict = self.open_api_dict['paths'].setdefault(path, {})
                method_set: set = pait_model.method_set
                for method in method_set:
                    method_dict: dict = path_dict.setdefault(method.lower(), {})
                    method_dict['summary'] = pait_model.desc
                    method_dict['operationId']: pait_model.operation_id
                    parameters_list: list = method_dict.setdefault('parameters', [])
                    request_body_dict: dict = method_dict.setdefault('requestBody', {})
                    response_dict: dict = method_dict.setdefault('responses', {})
                    all_field_dict = self._parse_func_param(pait_model.func)
                    for field, field_dict_list in all_field_dict.items():
                        if field in (
                                pait_field.Cookies.__name__.lower(), pait_field.Headers.__name__.lower(),
                                pait_field.Path.__name__.lower(), pait_field.Query.__name__.lower()
                        ):
                            for field_dict in field_dict_list:
                                parameters_list.append(
                                    {
                                        'name': field_dict['_param_name'],
                                        'in': field.lower(),
                                        'required': field_dict['default'] is Undefined,
                                        'description': field_dict['description'],
                                        'schema': field_dict['schema'],
                                        'type': field_dict['type']
                                    }
                                )
                        elif field == pait_field.Body.__name__.lower():
                            for field_dict in field_dict_list:
                                print(field_dict['schema'])
                        else:
                            # TODO
                            pass
                    if pait_model.response_model_list:
                        for resp_model_class in pait_model.response_model_list:
                            resp_model = resp_model_class()
                            schema_dict: dict = resp_model.response_data.schema()
                            path: str = f"#/components/schemas/{schema_dict['title']}"
                            self.change_ref(schema_dict, path)
                            for _status_code in resp_model.status_code:
                                response_dict[_status_code] = {
                                    'description': resp_model.description,
                                    'content': {
                                        resp_model.media_type: {"$ref": path}
                                    }
                                }
                                self.open_api_dict['components']['schema'].update({schema_dict['title']: schema_dict})
