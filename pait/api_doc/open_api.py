import copy
import json
import logging
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
from pait.util import create_pydantic_model, get_model_global_name, pait_model_schema

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

    url: str = Field("http://127.0.0.1")
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
            _OpenApiInfoModel(**open_api_info)

        if not open_api_server_list:
            open_api_server_list = [_OpenApiServerModel().dict(exclude_none=True)]
        else:
            temp_open_api_server_list: List[Dict[str, Any]] = []
            for open_api_server in open_api_server_list:
                _OpenApiServerModel(**open_api_server)
                temp_open_api_server_list.append(open_api_server)

            open_api_server_list = temp_open_api_server_list

        if not open_api_tag_list:
            open_api_tag_list = []
        else:
            temp_open_api_tag_list: List[Dict[str, Any]] = []
            for open_api_tag in open_api_tag_list:
                _OpenApiTagModel(**open_api_tag)
                temp_open_api_tag_list.append(open_api_tag)
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

    def _replace_pydantic_definitions(self, schema: dict, parent_schema: Optional[dict] = None) -> None:
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
                self._replace_pydantic_definitions(value, parent_schema)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._replace_pydantic_definitions(item, parent_schema)

    @staticmethod
    def _snake_name_to_hump_name(name: str) -> str:
        return "".join([item.capitalize() for item in name.split("_")])

    @staticmethod
    def _field_list_2_file_upload(
        media_type: str,
        openapi_method_dict: dict,
        field_dict_list: List[FieldSchemaTypeDict],
    ) -> None:
        """https://swagger.io/docs/specification/describing-request-body/file-upload/"""
        openapi_request_body_dict: dict = openapi_method_dict.setdefault("requestBody", {"content": {}})
        required_column_list: List[str] = [
            field_dict["raw"]["param_name"] for field_dict in field_dict_list if field_dict["default"] is Undefined
        ]
        properties_dict: dict = {
            field_dict["raw"]["param_name"]: {
                "title": field_dict["raw"]["param_name"].capitalize(),
                "type": "string",
                "format": "binary",
            }
            for field_dict in field_dict_list
        }
        if not openapi_request_body_dict.get("required", False):
            if required_column_list:
                openapi_request_body_dict["required"] = True
        if media_type not in openapi_request_body_dict["content"]:
            openapi_request_body_dict["content"][media_type] = {
                "schema": {"type": "object", "properties": properties_dict, "required": required_column_list}
            }
        else:
            openapi_request_body_dict["content"][media_type]["schema"]["properties"].update(properties_dict)
            openapi_request_body_dict["content"][media_type]["schema"]["required"].extend(required_column_list)

    def _field_list_2_request_body(
        self,
        field_class: Type[pait_field.BaseField],
        openapi_method_dict: dict,
        field_dict_list: List[FieldSchemaTypeDict],
        operation_id: str,
    ) -> None:
        """
        gen request body schema and update request body schemas'definitions to components schemas
        Ps: Minimize the use of components, because the user may use the same name of the model
          but the feature is different
        Doc: https://swagger.io/docs/specification/describing-request-body/
        """
        openapi_request_body_dict: dict = openapi_method_dict.setdefault("requestBody", {"content": {}})
        annotation_dict: Dict[str, Tuple[Type, pait_field.BaseField]] = {
            field_dict["raw"]["param_name"]: (field_dict["raw"]["annotation"], field_dict["raw"]["field"])
            for field_dict in field_dict_list
        }
        _pydantic_model: Type[BaseModel] = create_pydantic_model(
            annotation_dict, class_name=f"{self._snake_name_to_hump_name(operation_id)}DynamicModel"
        )
        schema_dict = copy.deepcopy(_pydantic_model.schema())
        self._replace_pydantic_definitions(schema_dict)
        if "definitions" in schema_dict:
            del schema_dict["definitions"]
        if field_class.media_type in openapi_request_body_dict["content"]:
            for key, value in openapi_request_body_dict["content"][field_class.media_type]["schema"].items():
                if isinstance(value, list):
                    value.extend(schema_dict[key])
                elif isinstance(value, dict):
                    value.update(schema_dict[key])
        else:
            openapi_request_body_dict["content"][field_class.media_type] = {"schema": schema_dict}

        if field_class == pait_field.MultiForm:
            if pait_field.File.media_type in openapi_request_body_dict["content"]:
                logging.warning(f"Swagger UI could not support {operation_id} MultiForm")
            form_encoding_dict = openapi_request_body_dict["content"][field_class.media_type].setdefault("encoding", {})
            for field_dict in field_dict_list:
                form_encoding_dict[field_dict["raw"]["param_name"]] = field_class.openapi_serialization
            # TODO support payload?
            # https://swagger.io/docs/specification/describing-request-body/
            if pait_field.MultiForm.media_type in openapi_request_body_dict["content"]:
                logging.warning(f"Swagger UI could not support {operation_id} MultiForm")

    # flake8: noqa: C901
    def parse_data_2_openapi(self) -> None:
        for group, pait_model_list in self._group_pait_dict.items():
            for pait_model in pait_model_list:
                path: str = pait_model.openapi_path
                openapi_path_dict: dict = self.open_api_dict["paths"].setdefault(path, {})
                for method in pait_model.method_list:
                    # Documentation for each route
                    openapi_method_dict: dict = openapi_path_dict.setdefault(method.lower(), {})
                    openapi_method_dict["group"] = group  # Not an openapi standard parameter
                    if pait_model.tag:
                        openapi_method_dict["tags"] = list(pait_model.tag)
                        # Additional labeling instructions
                        for tag in pait_model.tag:
                            if tag not in {tag_dict["name"] for tag_dict in self.open_api_dict["tags"]}:
                                logging.warning(f"Can not found tag:{tag} description, set default description")
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

                    # Initialize variables
                    openapi_parameters_list: list = openapi_method_dict.setdefault("parameters", [])
                    openapi_response_dict: dict = openapi_method_dict.setdefault("responses", {})
                    # Extracting request and response information through routing functions
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
                            pait_field.MultiQuery,
                        ):
                            for field_dict in field_dict_list:
                                param_name: str = field_dict["raw"]["param_name"]
                                required: bool = field_dict["default"] is Undefined
                                # openapi description must not null, but Field().description value is None
                                description: str = field_dict["description"] or ""
                                if field_class == pait_field.Header:
                                    pass
                                    # I don't know why the swagger doc tells me to do a title name conversion
                                    #  when I don't actually need one
                                    # See: Header Parameters in
                                    #   https://swagger.io/docs/specification/describing-parameters/

                                    # param_name = self._header_keyword_dict.get(param_name, param_name)
                                elif field_class == pait_field.Path and not required:
                                    raise ValueError(
                                        "That path parameters must have required: true, "
                                        "because they are always required"
                                    )
                                elif field_class == pait_field.Cookie:
                                    if field_dict["raw"]["field"].raw_return:
                                        # fix swagger ui cookie type when pait_field.raw_return is True
                                        field_dict["raw"]["schema"]["type"] = "string"
                                    description += (
                                        " "
                                        "\n"
                                        ">Note for Swagger UI and Swagger Editor users: "
                                        " "
                                        "\n"
                                        ">Cookie authentication is"
                                        'currently not supported for "try it out" requests due to browser security'
                                        "restrictions. "
                                        "See [this issue](https://github.com/swagger-api/swagger-js/issues/1163)"
                                        "for more information. "
                                        "[SwaggerHub](https://swagger.io/tools/swaggerhub/)"
                                        "does not have this limitation. "
                                    )

                                # When the required parameter is False and schema.default is empty,
                                # openapi will automatically read the value of schema.example
                                openapi_parameters_list.append(
                                    {
                                        "name": param_name,
                                        "in": field_class.get_field_name(),
                                        "required": required,
                                        "description": description,
                                        "schema": field_dict["raw"]["schema"],
                                    }
                                )
                        elif field_class in (pait_field.Body, pait_field.Form, pait_field.MultiForm):
                            self._field_list_2_request_body(
                                field_class, openapi_method_dict, field_dict_list, pait_model.operation_id
                            )
                        elif field_class in (pait_field.File,):
                            self._field_list_2_file_upload(field_class.media_type, openapi_method_dict, field_dict_list)
                        else:
                            logging.warning(f"Pait not support field:{field_class}")

                    if pait_model.response_model_list:
                        response_schema_dict: Dict[tuple, List[Dict[str, str]]] = {}
                        for resp_model_class in pait_model.response_model_list:
                            resp_model: PaitResponseModel = resp_model_class()
                            global_model_name: str = ""
                            if resp_model.response_data:
                                global_model_name = get_model_global_name(resp_model.response_data)

                                schema_dict: dict = copy.deepcopy(pait_model_schema(resp_model.response_data))
                                self._replace_pydantic_definitions(schema_dict)
                                if "definitions" in schema_dict:
                                    # fix del schema dict
                                    del schema_dict["definitions"]
                                self.open_api_dict["components"]["schemas"].update({global_model_name: schema_dict})

                            for _status_code in resp_model.status_code:
                                key: tuple = (_status_code, resp_model.media_type)
                                if _status_code in openapi_response_dict:
                                    if resp_model.description:
                                        openapi_response_dict[_status_code][
                                            "description"
                                        ] += f"|{resp_model.description}"
                                else:
                                    openapi_response_dict[_status_code] = {"description": resp_model.description or ""}
                                if global_model_name:
                                    ref_dict: dict = {"$ref": f"#/components/schemas/{global_model_name}"}
                                    if key in response_schema_dict:
                                        response_schema_dict[key].append(ref_dict)
                                    else:
                                        response_schema_dict[key] = [ref_dict]
                        # mutli response support
                        # only response example see https://swagger.io/docs/specification/describing-responses/   FAQ
                        for key_tuple, path_list in response_schema_dict.items():
                            status_code, media_type = key_tuple
                            if len(path_list) == 1:
                                ref_dict = path_list[0]
                            else:
                                ref_dict = {"oneOf": path_list}
                            openapi_response_dict[status_code]["content"] = {media_type: {"schema": ref_dict}}
