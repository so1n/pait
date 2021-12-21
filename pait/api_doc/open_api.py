import copy
import json
from typing import Any, Dict, List, Optional, Tuple, Type

import yaml  # type: ignore
from pydantic import BaseModel, Field, HttpUrl
from pydantic.fields import Undefined

from pait import field as pait_field
from pait.api_doc.base_parse import PaitBaseParse
from pait.g import config
from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus
from pait.util import create_pydantic_model

from .base_parse import FieldDictType, FieldSchemaTypeDict

__all__ = ["PaitOpenApi"]


class _OpenApiInfoModel(BaseModel):
    """open api info column model"""

    class _Contact(BaseModel):
        name: str
        url: str
        email: str

    class _License(BaseModel):
        name: str
        url: str

    title: str = Field("Pait Open Api")
    description: str = Field(None)
    version: str = Field("0.0.1")
    contact: _Contact = Field(None)
    license: _License = Field(None)


class _OpenApiTagModel(BaseModel):
    """openapi tag column model"""

    class _ExternalDocs(BaseModel):
        url: HttpUrl

    name: str
    description: str = Field(None)
    externalDocs: str = Field(None)


class _OpenApiServerModel(BaseModel):
    """openapi server column model"""

    url: HttpUrl = Field("http://127.0.0.1")
    description: str = Field(None)


class PaitOpenApi(PaitBaseParse):
    def __init__(
        self,
        pait_dict: Dict[str, PaitCoreModel],
        title: Optional[str] = None,
        open_api_info: Optional[Dict[str, Any]] = None,
        open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
        open_api_server_list: Optional[List[Dict[str, Any]]] = None,
        # default_response: Optional[...] = None,  # TODO
        type_: str = "json",
    ):
        super().__init__(pait_dict)
        self._header_keyword_dict: Dict[str, str] = {
            "Content-Type": "requestBody.content.<media-type>",
            "Accept": "responses.<code>.content.<media-type>",
            "Authorization": " security",
        }

        if not open_api_info:
            open_api_info = _OpenApiInfoModel(title=title).dict(exclude_none=True)
        else:
            open_api_info = _OpenApiInfoModel(**open_api_info).dict()

        if not open_api_server_list:
            open_api_server_list = [_OpenApiServerModel().dict(exclude_none=True)]
        else:
            temp_open_api_server_list: List[Dict[str, Any]] = []
            for open_api_server in open_api_server_list:
                temp_open_api_server_list.append(_OpenApiServerModel(**open_api_server).dict(exclude_none=True))
            open_api_server_list = temp_open_api_server_list

        if not open_api_tag_list:
            open_api_tag_list = []
        else:
            temp_open_api_tag_list: List[Dict[str, Any]] = []
            for open_api_tag in open_api_tag_list:
                temp_open_api_tag_list.append(_OpenApiTagModel(**open_api_tag).dict(exclude_none=True))
            open_api_tag_list = temp_open_api_tag_list

        self.open_api_dict: Dict[str, Any] = {
            "openapi": "3.0.0",
            "info": open_api_info,
            "servers": open_api_server_list,
            "tags": open_api_tag_list,
            "paths": {},
            "components": {"schemas": {}},
            # TODO
            # "security": {},
            # "externalDocs": {}
        }
        self.parse_data_2_openapi()
        if type_ == "json":
            self.content = json.dumps(self.open_api_dict, cls=config.json_encoder)
            self._content_type = ".json"
        elif type_ == "yaml":
            self.content = yaml.dump(self.open_api_dict, sort_keys=False)
            self._content_type = ".yaml"

    def _replace_pydantic_definitions(self, schema: dict, path: str, parent_schema: Optional[dict] = None) -> None:
        """update schemas'definitions to components schemas"""
        if not parent_schema:
            parent_schema = schema
        for key, value in schema.items():
            if key == "$ref" and not value.startswith("#/components"):
                index: int = value.rfind("/") + 1
                model_key: str = value[index:]
                schema[key] = f"#/components/schemas/{model_key}"
                self.open_api_dict["components"]["schemas"][model_key] = parent_schema["definitions"][model_key]
            elif isinstance(value, dict):
                self._replace_pydantic_definitions(value, path, parent_schema)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._replace_pydantic_definitions(item, path, parent_schema)

    @staticmethod
    def _snake_name_to_hump_name(name: str) -> str:
        return "".join([item.upper() for item in name.split("_")])

    def _field_list_2_request_body(
        self,
        media_type: str,
        openapi_method_dict: dict,
        field_dict_list: List[FieldSchemaTypeDict],
        operation_id: str,
    ) -> None:
        """gen request body schema and update request body schemas'definitions to components schemas"""
        openapi_request_body_dict: dict = openapi_method_dict.setdefault("requestBody", {"content": {}})
        annotation_dict: Dict[str, Tuple[Type, pait_field.BaseField]] = {
            field_dict["raw"]["param_name"]: (field_dict["raw"]["annotation"], field_dict["raw"]["field"])
            for field_dict in field_dict_list
        }
        _pydantic_model: Type[BaseModel] = create_pydantic_model(
            annotation_dict, class_name=f"{self._snake_name_to_hump_name(operation_id)}DynamicModel"
        )
        schema_dict = copy.deepcopy(_pydantic_model.schema())
        path = f"#/components/schemas/{schema_dict['title']}"
        self._replace_pydantic_definitions(schema_dict, path)
        if "definitions" in schema_dict:
            del schema_dict["definitions"]

        openapi_request_body_dict["content"].update({media_type: {"schema": schema_dict}})

    # flake8: noqa: C901
    def parse_data_2_openapi(self) -> None:
        for group, pait_model_list in self._group_pait_dict.items():
            for pait_model in pait_model_list:
                path: str = pait_model.openapi_path
                openapi_path_dict: dict = self.open_api_dict["paths"].setdefault(path, {})
                for method in pait_model.method_list:
                    openapi_method_dict: dict = openapi_path_dict.setdefault(method.lower(), {})
                    if pait_model.tag:
                        openapi_method_dict["tags"] = list(pait_model.tag)
                        for tag in pait_model.tag:
                            if tag not in {tag_dict["name"] for tag_dict in self.open_api_dict["tags"]}:
                                self.open_api_dict["tags"].append(
                                    {
                                        "name": tag,
                                        "description": "",
                                    }
                                )
                    if pait_model.status in (
                        PaitStatus.abnormal,
                        PaitStatus.maintenance,
                        PaitStatus.archive,
                        PaitStatus.abandoned,
                    ):
                        openapi_method_dict["deprecated"] = True
                    openapi_method_dict["summary"] = pait_model.summary
                    openapi_method_dict["description"] = pait_model.desc
                    openapi_method_dict["operationId"] = f"{method}.{pait_model.operation_id}"
                    openapi_parameters_list: list = openapi_method_dict.setdefault("parameters", [])
                    openapi_response_dict: dict = openapi_method_dict.setdefault("responses", {})
                    all_field_dict: FieldDictType = self._parse_func_param_to_field_dict(pait_model.func)
                    for pre_depend in pait_model.pre_depend_list:
                        for field_class, field_dict_list in self._parse_func_param_to_field_dict(pre_depend).items():
                            if field_class not in all_field_dict:
                                all_field_dict[field_class] = field_dict_list
                            else:
                                all_field_dict[field_class].extend(field_dict_list)

                    for field_class, field_dict_list in all_field_dict.items():
                        if field_class in (
                            pait_field.Cookie,
                            pait_field.Header,
                            pait_field.Path,
                            pait_field.Query,
                        ):
                            for field_dict in field_dict_list:
                                param_name: str = field_dict["raw"]["param_name"]
                                if field_class == pait_field.Header:
                                    param_name = self._header_keyword_dict.get(param_name, param_name)
                                # TODO support example
                                openapi_parameters_list.append(
                                    {
                                        "name": param_name,
                                        "in": field_class.cls_lower_name(),
                                        "required": field_dict["default"] is Undefined,
                                        # openapi description must not null
                                        "description": field_dict["description"] or "",
                                        "schema": field_dict["raw"]["schema"],
                                    }
                                )
                        elif field_class == pait_field.Body:
                            # support args BodyField
                            self._field_list_2_request_body(
                                "application/json", openapi_method_dict, field_dict_list, pait_model.operation_id
                            )
                        elif field_class == pait_field.Form:
                            # support args FormField
                            self._field_list_2_request_body(
                                "application/x-www-form-urlencoded",
                                openapi_method_dict,
                                field_dict_list,
                                pait_model.operation_id,
                            )
                        else:
                            # TODO
                            pass

                    if pait_model.response_model_list:
                        response_schema_dict: Dict[tuple, List[Dict[str, str]]] = {}
                        for resp_model_class in pait_model.response_model_list:
                            resp_model: PaitResponseModel = resp_model_class()
                            schema_dict: dict = {}
                            if resp_model.response_data:
                                schema_dict = resp_model.response_data.schema()

                            # fix del schema dict
                            schema_dict = copy.deepcopy(schema_dict)
                            path = f"#/components/schemas/{schema_dict['title']}"
                            self._replace_pydantic_definitions(schema_dict, path)
                            if "definitions" in schema_dict:
                                del schema_dict["definitions"]
                            for _status_code in resp_model.status_code:
                                key: tuple = (_status_code, resp_model.media_type)
                                ref_dict: dict = {"$ref": path}
                                if key in response_schema_dict:
                                    response_schema_dict[key].append(ref_dict)
                                else:
                                    response_schema_dict[key] = [ref_dict]
                                if _status_code in openapi_response_dict:
                                    openapi_response_dict[_status_code]["description"] += f"|{resp_model.description}"
                                else:
                                    openapi_response_dict[_status_code] = {"description": resp_model.description}
                                self.open_api_dict["components"]["schemas"].update({schema_dict["title"]: schema_dict})
                        # mutli response support
                        # only response example see https://swagger.io/docs/specification/describing-responses/   FAQ
                        for key_tuple, path_list in response_schema_dict.items():
                            status_code, media_type = key_tuple
                            if len(path_list) == 1:
                                ref_dict = path_list[0]
                            else:
                                ref_dict = {"oneOf": path_list}
                            openapi_response_dict[status_code]["content"] = {media_type: {"schema": ref_dict}}
