import json
import yaml
from typing import Any, Dict, List, Type, Optional

from pydantic import BaseModel, Field, HttpUrl, create_model
from pydantic.fields import Undefined

from .base_parse import PaitBaseParse
from pait import field as pait_field
from pait.model import PaitStatus


__all__ = ['PaitOpenApi']


class _OpenApiInfoModel(BaseModel):
    class _Contact(BaseModel):
        name: str
        url: str
        email: str

    class _License(BaseModel):
        name: str
        url: str

    title: str = Field('Pait Open Api')
    description: str = Field(None)
    version: str = Field('0.0.1')
    contact: _Contact = Field(None)
    license: _License = Field(None)


class _OpenApiServerModel(BaseModel):
    url: HttpUrl = Field('http://127.0.0.1')
    description: str = Field(None)


class PaitOpenApi(PaitBaseParse):
    def __init__(
            self,
            filename: Optional[str] = None,
            open_api_info: Optional[Dict[str, Any]] = None,
            open_api_server_list: Optional[List[Dict[str, Any]]] = None,
            # default_response: Optional[...] = None,  # TODO
            _type: str = 'json'
    ):
        super().__init__()
        if not open_api_info:
            open_api_info = _OpenApiInfoModel().dict(exclude_none=True)
        else:
            _OpenApiInfoModel(**open_api_info).dict()

        if not open_api_server_list:
            open_api_server_list = [_OpenApiServerModel().dict(exclude_none=True)]
        else:
            for open_api_server in open_api_server_list:
                _OpenApiServerModel(**open_api_server)

        self.open_api_dict = {
            "openapi": "3.0.0",
            "info": open_api_info,
            "servers": open_api_server_list,
            "tags": [],
            "paths": {},
            "components": {"schemas": {}},
            # TODO
            # "security": {},
            # "externalDocs": {}
        }
        self.parse_data_2_openapi()
        if _type == 'json':
            pait_json: str = json.dumps(self.open_api_dict)
            self.output_file(filename, pait_json, '.json')
        elif _type == 'yaml':
            pait_yaml: str = yaml.dump(self.open_api_dict, sort_keys=False)
            self.output_file(filename, pait_yaml, '.yaml')

    def replace_pydantic_definitions(self, schema, path, parent_schema=None):
        if not parent_schema:
            parent_schema = schema
        for key, value in schema.items():
            if key == '$ref' and not value.startswith('#/components'):
                index: int = value.rfind('/') + 1
                model_key: str = value[index:]
                schema[key] = f"#/components/schemas/{model_key}"
                self.open_api_dict['components']['schemas'][model_key] = parent_schema['definitions'][model_key]
            if type(value) is dict:
                self.replace_pydantic_definitions(value, path, parent_schema)

    @staticmethod
    def field_2_request_body(media_type: str, method_dict: dict, field_dict_list: List[dict]):
        request_body_dict: dict = method_dict.setdefault('requestBody', {"content": {}})

        annotation_dict: Dict[str, Type] = {
            field_dict['raw']['param_name']: (
                field_dict['raw']['annotation'], field_dict['raw']['field']
            )
            for field_dict in field_dict_list
        }
        _pydantic_model: Type[BaseModel] = create_model('DynamicFoobarModel', **annotation_dict)
        request_body_dict["content"].update(
            {
                media_type: {
                    "schema": _pydantic_model.schema()
                }
            }
        )

    def parse_data_2_openapi(self):
        for group, pait_model_list in self._tag_pait_dict.items():
            for pait_model in pait_model_list:
                path: str = pait_model.path
                path_dict: dict = self.open_api_dict['paths'].setdefault(path, {})
                method_set: set = pait_model.method_set
                for method in method_set:
                    method_dict: dict = path_dict.setdefault(method.lower(), {})
                    if pait_model.tag:
                        method_dict['tags'] = list(pait_model.tag)
                        for tag in pait_model.tag:
                            tag_dict: dict = {
                                "name": tag,
                                "description": "",
                            }
                            if tag_dict not in self.open_api_dict['tags']:
                                self.open_api_dict['tags'].append(tag_dict)
                    if pait_model.status in (PaitStatus.archive, PaitStatus.abandoned):
                        method_dict['deprecated'] = True
                    method_dict['summary'] = pait_model.desc
                    method_dict['operationId']: pait_model.operation_id
                    parameters_list: list = method_dict.setdefault('parameters', [])
                    response_dict: dict = method_dict.setdefault('responses', {})
                    all_field_dict = self._parse_func_param(pait_model.func)

                    for field, field_dict_list in all_field_dict.items():
                        if field in (
                                pait_field.Cookie.__name__.lower(), pait_field.Header.__name__.lower(),
                                pait_field.Path.__name__.lower(), pait_field.Query.__name__.lower()
                        ):
                            for field_dict in field_dict_list:
                                parameters_list.append(
                                    {
                                        'name': field_dict['raw']['param_name'],
                                        'in': field.lower(),
                                        'required': field_dict['default'] is Undefined,
                                        'description': field_dict['description'],
                                        'schema': field_dict['raw']['schema']
                                    }
                                )
                        elif field == pait_field.Body.__name__.lower():
                            # support args BodyField
                            self.field_2_request_body("application/json", method_dict, field_dict_list)
                        elif field == pait_field.Form.__name__.lower():
                            # support args FormField
                            self.field_2_request_body("application/x-www-form-urlencoded", method_dict, field_dict_list)
                        else:
                            # TODO
                            pass

                    if pait_model.response_model_list:
                        response_schema_dict: Dict[tuple, List[Dict[str, str]]] = {}
                        for resp_model_class in pait_model.response_model_list:
                            resp_model = resp_model_class()
                            schema_dict: dict = resp_model.response_data.schema()
                            path: str = f"#/components/schemas/{schema_dict['title']}"
                            self.replace_pydantic_definitions(schema_dict, path)
                            if 'definitions' in schema_dict:
                                del schema_dict['definitions']
                            for _status_code in resp_model.status_code:
                                key: tuple = (_status_code, resp_model.media_type)
                                ref_dict: dict = {"$ref": path}
                                if key in response_schema_dict:
                                    response_schema_dict[key].append(ref_dict)
                                else:
                                    response_schema_dict[key] = [ref_dict]
                                if _status_code in response_dict:
                                    response_dict[_status_code]['description'] += f'|{resp_model.description}'
                                else:
                                    response_dict[_status_code] = {'description': resp_model.description}
                                self.open_api_dict['components']['schemas'].update({schema_dict['title']: schema_dict})
                        # mutli response support
                        # only response example see https://swagger.io/docs/specification/describing-responses/   FAQ
                        for key_tuple, path_list in response_schema_dict.items():
                            status_code, media_type = key_tuple
                            if len(path_list) == 1:
                                ref_dict: dict = path_list[0]
                            else:
                                ref_dict: dict = {'oneOf': path_list}
                            response_dict[status_code]['content'] = {
                                media_type: {"schema": ref_dict}
                            }
