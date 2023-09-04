import inspect
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from any_api.openapi import ApiModel as _ApiModel
from any_api.openapi import ExternalDocumentationModel, HttpParamTypeLiteral, InfoModel
from any_api.openapi import OpenAPI as _OpenAPI
from any_api.openapi import SecurityModelType, ServerModel, TagModel, openapi_model
from any_api.openapi.model.links import LinksModel
from any_api.openapi.model.openapi import OpenAPIModel
from any_api.openapi.model.requests import RequestModel
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

from pait import _pydanitc_adapter
from pait.app.any.util import import_func_from_app
from pait.data import PaitCoreProxyModel
from pait.field import BaseRequestResourceField, Depends
from pait.g import config
from pait.model.core import PaitCoreModel
from pait.param_handle.util import get_parameter_list_from_class
from pait.types import CallType
from pait.util import FuncSig, create_pydantic_model, get_func_sig

HttpParamTypeDictType = Dict[HttpParamTypeLiteral, List[RequestModel]]


__all__ = ["LinksModel", "ApiModel", "ParsePaitModel", "OpenAPI"]


class ApiModel(_ApiModel):
    pait_core_model: PaitCoreModel = Field()

    if _pydanitc_adapter.is_v1:

        class Config:
            arbitrary_types_allowed = True

    else:
        model_config: _pydanitc_adapter.ConfigDict = _pydanitc_adapter.ConfigDict(arbitrary_types_allowed=True)

    def add_to_operation_model(self, _openapi_model: openapi_model.OperationModel) -> None:
        # Not an openapi standard parameter
        _openapi_model.pait_info = {
            "group": self.pait_core_model.group,
            "status": self.pait_core_model.status.value,
            "author": self.pait_core_model.author,
            "pait_id": self.pait_core_model.pait_id,
        }


class ParsePaitModel(object):
    def __init__(self, pait_model: PaitCoreModel) -> None:
        self.pait_model: PaitCoreModel = pait_model
        self.http_param_type_dict: HttpParamTypeDictType = {}
        self.security_dict: Dict[str, openapi_model.security.SecurityModelType] = {}
        self.http_param_type_alias_dict: Dict[str, HttpParamTypeLiteral] = {"multiquery": "query"}

        self.param_field_dict: Dict[str, BaseRequestResourceField] = {}
        self.http_param_type_annotation_dict: Dict[HttpParamTypeLiteral, Dict[str, Tuple[Type, FieldInfo]]] = {}

        for extra_openapi_model in self.pait_model.extra_openapi_model_list:
            self._parse_base_model(extra_openapi_model)
        for pre_depend in pait_model.pre_depend_list:
            self._parse_call_type(pre_depend)
        self._parse_call_type(pait_model.func)

        for http_param_type, annotation_dict in self.http_param_type_annotation_dict.items():
            http_param_type = self.http_param_type_alias_dict.get(http_param_type, http_param_type)
            if http_param_type not in self.http_param_type_dict:
                self.http_param_type_dict[http_param_type] = []
            self.http_param_type_dict[http_param_type].append(
                RequestModel(
                    description="",
                    media_type_list=[self.param_field_dict[http_param_type].media_type],
                    openapi_serialization=self.param_field_dict[http_param_type].openapi_serialization,
                    model=create_pydantic_model(
                        annotation_dict,
                        class_name=(
                            f"{self.pait_model.func_name.title()}{self.pait_model.pait_id.title()}"
                            f"{http_param_type.title()}HttpParamModel"
                        ),
                    ),
                )
            )

    def _parse_base_model(
        self, _pydantic_model: Type[BaseModel], default_field_class: Optional[Type[BaseRequestResourceField]] = None
    ) -> None:
        from typing import get_type_hints

        for field_name, model_field in _pydanitc_adapter.model_fields(_pydantic_model).items():
            param_annotation = get_type_hints(_pydantic_model)[field_name]
            field = _pydanitc_adapter.get_field_info(model_field)
            if not isinstance(field, BaseRequestResourceField):
                if self.pait_model.default_field_class:
                    field = self.pait_model.default_field_class.from_pydantic_field(field)
                elif default_field_class:
                    field = default_field_class.from_pydantic_field(field)
                else:
                    continue
            if not field.openapi_include:
                continue
            if isinstance(field, BaseRequestResourceField) and field.alias:
                field_name = field.alias
            http_param_type: HttpParamTypeLiteral = field.get_field_name()  # type: ignore
            http_param_type = self.http_param_type_alias_dict.get(http_param_type, http_param_type)
            if http_param_type not in self.http_param_type_annotation_dict:
                self.http_param_type_annotation_dict[http_param_type] = {}
            self.http_param_type_annotation_dict[http_param_type][field_name] = (param_annotation, field)
            self.param_field_dict[http_param_type] = field

    def parameter_list_handle(
        self,
        parameter_list: List["inspect.Parameter"],
        single_field_list: List[Tuple[str, "inspect.Parameter"]],
    ) -> None:
        """parse parameter_list to field_dict and single_field_list"""
        for parameter in parameter_list:
            if parameter.default != parameter.empty:
                annotation: type = parameter.annotation
                pait_field: Union[BaseRequestResourceField, Depends] = parameter.default
                if (
                    inspect.isclass(annotation)
                    and issubclass(annotation, BaseModel)
                    and not isinstance(pait_field, Depends)
                ):
                    # support def test(pait_model_route: BaseModel = Body())
                    if not pait_field.openapi_include:
                        continue
                    if not pait_field.raw_return:
                        self._parse_base_model(
                            create_pydantic_model(
                                {parameter.name: (parameter.annotation, pait_field)},
                                class_name=(
                                    f"{self.pait_model.func_name.title()}{self.pait_model.pait_id.title()}"
                                    f"{parameter.name.title()}RawReturnModel"
                                ),
                            ),
                            pait_field.__class__,
                        )
                    else:
                        self._parse_base_model(annotation, pait_field.__class__)
                else:
                    # def test(pait_model_route: int = Body())
                    if isinstance(pait_field, Depends):
                        self._parse_call_type(pait_field.func)
                    else:
                        if not pait_field.openapi_include:
                            continue
                        field_name: str = pait_field.__class__.__name__.lower()
                        single_field_list.append((field_name, parameter))

            elif inspect.isclass(parameter.annotation) and issubclass(parameter.annotation, BaseModel):
                # def test(pait_model_route: PaitBaseModel)
                self._parse_base_model(parameter.annotation)

    def _parse_call_type(self, call_type: CallType) -> None:
        from pait.app.base.security.base import BaseSecurity

        if isinstance(call_type, BaseSecurity):
            if self.security_dict.get(call_type.security_name, None) not in (call_type.model, None):
                raise ValueError(
                    f"{call_type.security_name}Already exists, "
                    f"but the Security Model is inconsistent with {call_type.model}"
                )
            self.security_dict[call_type.security_name] = call_type.model

        func_type_sig: FuncSig = get_func_sig(call_type)
        single_field_list: List[Tuple[str, "inspect.Parameter"]] = []

        qualname: str = getattr(call_type, "__qualname__", "")
        if not qualname:
            class_ = call_type.__class__  # type: ignore
        else:
            qualname = qualname.split(".<locals>", 1)[0].rsplit(".", 1)[0]
            class_ = getattr(inspect.getmodule(call_type), qualname)

        if inspect.isclass(class_):
            parameter_list: List["inspect.Parameter"] = get_parameter_list_from_class(class_)
            self.parameter_list_handle(parameter_list, single_field_list)
        self.parameter_list_handle(func_type_sig.param_list, single_field_list)

        if single_field_list:
            annotation_dict: Dict[str, Tuple[Type, Any]] = {}
            _column_name_set: Set[str] = set()
            for field_name, parameter in single_field_list:
                field: BaseRequestResourceField = parameter.default
                key: str = field.alias or parameter.name
                if key in _column_name_set:
                    # Since the same name cannot exist together in a Dict,
                    #  it will be parsed directly when a Key exists
                    # fix
                    #  class Demo(BaseModel):
                    #      header_token: str = Header(alias="token")
                    #      query_token: str = Query(alias="token")
                    _pydantic_model: Type[BaseModel] = create_pydantic_model(
                        {parameter.name: (parameter.annotation, field)},
                        class_name=(
                            f"{self.pait_model.func_name.title()}"
                            f"{self.pait_model.pait_id.title()}{key.title()}SameNameModel"
                        ),
                    )
                    self._parse_base_model(_pydantic_model)
                else:
                    _column_name_set.add(key)
                    annotation_dict[parameter.name] = (parameter.annotation, field)

            _pydantic_model = create_pydantic_model(
                annotation_dict,
                class_name=(f"{self.pait_model.func_name.title()}{self.pait_model.pait_id.title()}SingleFieldModel"),
            )
            self._parse_base_model(_pydantic_model)


class OpenAPI(object):
    load_app: staticmethod

    def __init__(
        self,
        app: Any,
        undefined: Any = _pydanitc_adapter.PydanticUndefined,
        load_app: Optional[Callable] = None,
        openapi_info_model: Optional[InfoModel] = None,
        server_model_list: Optional[List[ServerModel]] = None,
        tag_model_list: Optional[List[TagModel]] = None,
        external_docs: Optional[ExternalDocumentationModel] = None,
        security_dict: Optional[Dict[str, SecurityModelType]] = None,
    ):
        self._undefined: Any = undefined
        self._openapi: _OpenAPI = _OpenAPI(
            openapi_info_model=openapi_info_model,
            server_model_list=server_model_list,
            tag_model_list=tag_model_list,
            external_docs=external_docs,
            security_dict=security_dict,
        )
        self._pait_dict: Dict[str, PaitCoreModel] = (
            load_app or getattr(self, "load_app", None) or import_func_from_app("load_app", app=app)  # type: ignore
        )(app)
        api_model_list: List[ApiModel] = []
        for pait_id, pait_model in self._pait_dict.items():
            pait_model = PaitCoreProxyModel.get_core_model(pait_model)
            try:
                parse_pait_model: ParsePaitModel = ParsePaitModel(pait_model)
                api_model_list.append(
                    ApiModel(
                        path=pait_model.openapi_path,
                        http_method_list=pait_model.openapi_method_list,
                        tags=[i.to_tag_model() for i in pait_model.tag],
                        operation_id=pait_model.operation_id,
                        summary=pait_model.summary,
                        request_dict=parse_pait_model.http_param_type_dict,
                        response_list=pait_model.response_model_list,
                        description=pait_model.desc,
                        deprecated=pait_model.status.is_deprecated(),
                        pait_core_model=pait_model,
                        security=parse_pait_model.security_dict,
                    )
                )
            except Exception as e:
                logging.error(f"parse pait model error by func: {pait_model.func_path}/{pait_model.func_name}")
                raise e
        # In order to be compatible with the link, it must be imported in batches
        self._openapi.add_api_model(*api_model_list)

    #########################
    # proxy openapi feature #
    #########################
    @property
    def model(self) -> OpenAPIModel:
        return self._openapi.model

    @property
    def dict(self) -> dict:
        return self._openapi.dict

    def content(self, serialization_callback: Callable = json.dumps, **kwargs: Any) -> str:
        if serialization_callback is json.dumps and "cls" not in kwargs:
            kwargs["cls"] = config.json_encoder
        return self._openapi.content(serialization_callback, **kwargs)
