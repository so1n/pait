import copy
import json
from typing import Any, Dict, List, Optional, Tuple, Type

import yaml
from pydantic import BaseModel, Field, HttpUrl
from pydantic.fields import Undefined

from pait import field as pait_field
from pait.api_doc.base_parse import PaitBaseParse
from pait.model import PaitCoreModel, PaitResponseModel, PaitStatus
from pait.util import create_pydantic_model

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
        self.parse_data_2_openapi(self.open_api_dict)
        if type_ == "json":
            self.content = json.dumps(self.open_api_dict)
            self._content_type = ".json"
        elif type_ == "yaml":
            self.content = yaml.dump(self.open_api_dict, sort_keys=False)
            self._content_type = ".yaml"

    def replace_pydantic_definitions(
        self, schema: dict, path: str, open_api_dict: Dict[str, Any], parent_schema: Optional[dict] = None
    ) -> None:
        if not parent_schema:
            parent_schema = schema
        for key, value in schema.items():
            if key == "$ref" and not value.startswith("#/components"):
                index: int = value.rfind("/") + 1
                model_key: str = value[index:]
                schema[key] = f"#/components/schemas/{model_key}"
                open_api_dict["components"]["schemas"][model_key] = parent_schema["definitions"][model_key]
            if type(value) is dict:
                self.replace_pydantic_definitions(value, path, open_api_dict, parent_schema)

    @staticmethod
    def field_2_request_body(media_type: str, method_dict: dict, field_dict_list: List[dict]) -> None:
        openapi_request_body_dict: dict = method_dict.setdefault("requestBody", {"content": {}})

        annotation_dict: Dict[str, Tuple[Type, Any]] = {
            field_dict["raw"]["param_name"]: (field_dict["raw"]["annotation"], field_dict["raw"]["field"])
            for field_dict in field_dict_list
        }
        _pydantic_model: Type[BaseModel] = create_pydantic_model(annotation_dict)
        openapi_request_body_dict["content"].update({media_type: {"schema": _pydantic_model.schema()}})

    def parse_data_2_openapi(self, open_api_dict: Dict[str, Any]) -> None:
        for group, pait_model_list in self._group_pait_dict.items():
            for pait_model in pait_model_list:
                path: str = pait_model.path
                openapi_path_dict: dict = open_api_dict["paths"].setdefault(path, {})
                method_list: list = pait_model.method_list
                for method in method_list:
                    openapi_method_dict: dict = openapi_path_dict.setdefault(method.lower(), {})
                    if pait_model.tag:
                        openapi_method_dict["tags"] = list(pait_model.tag)
                        for tag in pait_model.tag:
                            if tag not in {tag_dict["name"] for tag_dict in open_api_dict["tags"]}:
                                open_api_dict["tags"].append(
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
                    all_field_dict: Dict[str, List[Dict[str, Any]]] = self._parse_func_param_to_field_dict(
                        pait_model.func
                    )

                    for field, field_dict_list in all_field_dict.items():
                        if field in (
                            pait_field.Cookie.__name__.lower(),
                            pait_field.Header.__name__.lower(),
                            pait_field.Path.__name__.lower(),
                            pait_field.Query.__name__.lower(),
                        ):
                            for field_dict in field_dict_list:
                                param_name: str = field_dict["raw"]["param_name"]
                                if field == pait_field.Header.__name__.lower():
                                    param_name = self._header_keyword_dict.get(param_name, param_name)

                                # TODO support example
                                openapi_parameters_list.append(
                                    {
                                        "name": param_name,
                                        "in": field.lower(),
                                        "required": field_dict["default"] is Undefined,
                                        "description": field_dict["description"],
                                        "schema": field_dict["raw"]["schema"],
                                    }
                                )
                        elif field == pait_field.Body.__name__.lower():
                            # support args BodyField
                            self.field_2_request_body("application/json", openapi_method_dict, field_dict_list)
                        elif field == pait_field.Form.__name__.lower():
                            # support args FormField
                            self.field_2_request_body(
                                "application/x-www-form-urlencoded", openapi_method_dict, field_dict_list
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
                            self.replace_pydantic_definitions(schema_dict, path, open_api_dict)
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
                                open_api_dict["components"]["schemas"].update({schema_dict["title"]: schema_dict})
                        # mutli response support
                        # only response example see https://swagger.io/docs/specification/describing-responses/   FAQ
                        for key_tuple, path_list in response_schema_dict.items():
                            status_code, media_type = key_tuple
                            if len(path_list) == 1:
                                ref_dict = path_list[0]
                            else:
                                ref_dict = {"oneOf": path_list}
                            openapi_response_dict[status_code]["content"] = {media_type: {"schema": ref_dict}}
