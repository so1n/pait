import copy
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, Field, HttpUrl
from pydantic.fields import Undefined

from pait import field as pait_field
from pait.api_doc.base_parse import PaitBaseParse
from pait.g import config
from pait.model.core import PaitCoreModel
from pait.model.response import PaitBaseResponseModel
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
        for tag, desc in config.tag_dict.items():
            open_api_tag_list.append({"name": tag, "description": desc})

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
            import yaml  # type: ignore

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

    def _pait_model_2_response(
        self,
        pait_model: PaitCoreModel,
        openapi_method_dict: dict,
    ) -> None:
        openapi_response_dict: dict = openapi_method_dict.setdefault("responses", {})
        response_schema_dict: Dict[tuple, List[Dict[str, str]]] = {}
        for resp_model_class in pait_model.response_model_list:
            resp_model: PaitBaseResponseModel = resp_model_class()
            global_model_name: str = ""
            if isinstance(resp_model.response_data, type) and issubclass(resp_model.response_data, BaseModel):
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
                        openapi_response_dict[_status_code]["description"] += f"|{resp_model.description}"
                    if resp_model.header:
                        openapi_response_dict[_status_code]["headers"].update(resp_model.header)
                else:
                    openapi_response_dict[_status_code] = {
                        "description": resp_model.description or "",
                        "headers": resp_model.header,
                    }
                if _status_code == 204:
                    # 204 No Content, have no body.
                    # To indicate the response body is empty, do not specify a content for the response
                    continue

                openapi_response_dict[_status_code]["content"] = {}
                if resp_model.links_schema_dict:
                    openapi_response_dict[_status_code]["links"] = resp_model.links_schema_dict

                if global_model_name:
                    openapi_schema_dict: dict = {"$ref": f"#/components/schemas/{global_model_name}"}
                    if key in response_schema_dict:
                        response_schema_dict[key].append(openapi_schema_dict)
                    else:
                        response_schema_dict[key] = [openapi_schema_dict]
                elif resp_model.openapi_schema:
                    if resp_model.media_type in openapi_response_dict[_status_code]["content"]:
                        raise ValueError(
                            f"{resp_model.media_type} already exists, "
                            f"Please check {pait_model.operation_id}'s "
                            f"response model list:{pait_model.response_model_list}"
                        )
                    openapi_response_dict[_status_code]["content"][resp_model.media_type] = resp_model.openapi_schema
                else:
                    logging.warning(
                        f"Can not found response schema from {pait_model.operation_id}'s response model:{resp_model}"
                    )

        # mutli response support
        # only response example see https://swagger.io/docs/specification/describing-responses/   FAQ
        for key_tuple, path_list in response_schema_dict.items():
            status_code, media_type = key_tuple
            if len(path_list) == 1:
                openapi_schema_dict = path_list[0]
            else:
                openapi_schema_dict = {"oneOf": path_list}
            openapi_response_dict[status_code]["content"] = {media_type: {"schema": openapi_schema_dict}}

    @staticmethod
    def _field_list_2_request_parameter(
        field_class: Type[pait_field.BaseField],
        openapi_method_dict: dict,
        field_dict_list: List[FieldSchemaTypeDict],
    ) -> None:
        openapi_parameters_list: list = openapi_method_dict.setdefault("parameters", [])
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
                raise ValueError("That path parameters must have required: true, " "because they are always required")
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

    @staticmethod
    def _field_list_2_file_upload(
        field_class: Type[pait_field.BaseField],
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
        if field_class.media_type not in openapi_request_body_dict["content"]:
            openapi_request_body_dict["content"][field_class.media_type] = {
                "schema": {"type": "object", "properties": properties_dict, "required": required_column_list}
            }
        else:
            openapi_request_body_dict["content"][field_class.media_type]["schema"]["properties"].update(properties_dict)
            openapi_request_body_dict["content"][field_class.media_type]["schema"]["required"].extend(
                required_column_list
            )

    def _field_list_2_request_body(
        self,
        field_class: Type[pait_field.BaseField],
        openapi_method_dict: dict,
        field_dict_list: List[FieldSchemaTypeDict],
        operation_id: str,
    ) -> None:
        """
        gen request body schema and update request body schemas'definitions to components schemas
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
        schema_dict = copy.deepcopy(pait_model_schema(_pydantic_model))
        # pait will disassemble and reassemble the BaseModel, so there is no way to reuse the model in openapi.
        # TODO support model
        # self._replace_pydantic_definitions(schema_dict)
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
            # pait_field.File must precede pait_field.MultiForm
            form_encoding_dict = openapi_request_body_dict["content"][field_class.media_type].setdefault("encoding", {})
            for field_dict in field_dict_list:
                if pait_field.File.media_type in openapi_request_body_dict["content"]:
                    openapi_request_body_dict["content"][field_class.media_type]["schema"]["properties"][
                        field_dict["raw"]["param_name"]
                    ]["description"] += (
                        " " " " "\n" f">Swagger UI could not support, when media_type is {pait_field.File.media_type}"
                    )
                form_encoding_dict[field_dict["raw"]["param_name"]] = field_class.openapi_serialization
            # TODO support payload?
            # https://swagger.io/docs/specification/describing-request-body/

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
                                logging.warning(
                                    f"Can not found tag:{tag} description, set default description, "
                                    f"you can use pait.model.tag.Tag({tag}, desc='')"
                                )
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

                    all_field_dict: FieldDictType = self._parse_pait_model_to_field_dict(pait_model)
                    all_field_class_list: List[Type[pait_field.BaseField]] = sorted(
                        [i for i in all_field_dict.keys()], key=lambda x: x.get_field_name()
                    )
                    for field_class in all_field_class_list:
                        field_dict_list = all_field_dict[field_class]
                        if field_class in (
                            pait_field.Cookie,
                            pait_field.Header,
                            pait_field.Path,
                            pait_field.Query,
                            pait_field.MultiQuery,
                        ):
                            self._field_list_2_request_parameter(field_class, openapi_method_dict, field_dict_list)
                        elif field_class in (pait_field.Body, pait_field.Form, pait_field.MultiForm):
                            self._field_list_2_request_body(
                                field_class, openapi_method_dict, field_dict_list, pait_model.operation_id
                            )
                        elif field_class in (pait_field.File,):
                            self._field_list_2_file_upload(field_class, openapi_method_dict, field_dict_list)
                        else:
                            logging.warning(f"Pait not support field:{field_class}")

                    if pait_model.response_model_list:
                        self._pait_model_2_response(pait_model, openapi_method_dict)
