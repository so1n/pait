import inspect
import json
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from any_api.openapi import ApiModel as _ApiModel
from any_api.openapi import ExternalDocumentationModel, HttpParamTypeLiteral, InfoModel
from any_api.openapi import OpenAPI as _OpenAPI
from any_api.openapi import SecurityModelType, ServerModel, TagModel, openapi_model
from any_api.openapi.model.openapi import OpenAPIModel
from any_api.openapi.model.request_model import RequestModel
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo, Undefined

from pait.field import BaseField, Depends
from pait.g import config
from pait.model.core import PaitCoreModel
from pait.model.status import PaitStatus
from pait.util import FuncSig, create_pydantic_model, get_func_sig, get_parameter_list_from_class

HttpParamTypeDictType = Dict[HttpParamTypeLiteral, List[RequestModel]]


class ApiModel(_ApiModel):
    pait_core_model: PaitCoreModel = Field()

    class Config:
        arbitrary_types_allowed = True

    def add_to_operation_model(self, _openapi_model: openapi_model.OperationModel) -> None:
        # Not an openapi standard parameter
        _openapi_model.pait_info = {
            "group": self.pait_core_model.group,
            "status": self.pait_core_model.status.value,
            "author": self.pait_core_model.author,
            "md5": self.pait_core_model.func_md5,
        }


class OpenAPI(object):
    def __init__(
        self,
        pait_dict: Dict[str, PaitCoreModel],
        undefined: Any = Undefined,
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
        api_model_list: List[ApiModel] = []
        for pait_id, pait_model in pait_dict.items():
            http_param_type_dict: HttpParamTypeDictType = self._parse_pait_model_to_http_param_type_dict(pait_model)
            api_model_list.append(
                ApiModel(
                    path=pait_model.openapi_path,
                    http_method_list=pait_model.openapi_method_list,
                    tags=[i.to_tag_model() for i in pait_model.tag],
                    operation_id=pait_model.operation_id,
                    summary=pait_model.summary,
                    request_dict=http_param_type_dict,
                    response_list=pait_model.response_model_list,
                    description=pait_model.desc,
                    deprecated=pait_model.status
                    in (
                        PaitStatus.abnormal,
                        PaitStatus.maintenance,
                        PaitStatus.archive,
                        PaitStatus.abandoned,
                    ),
                    pait_core_model=pait_model,
                )
            )
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

    def _parse_base_model_to_http_param_type_dict(
        self, http_param_type_dict: HttpParamTypeDictType, _pydantic_model: Type[BaseModel]
    ) -> None:
        param_field_dict: Dict[str, BaseField] = {}
        http_param_type_annotation_dict: Dict[HttpParamTypeLiteral, Dict[str, Tuple[Type, FieldInfo]]] = {}
        from typing import get_type_hints

        for field_name, model_field in _pydantic_model.__fields__.items():
            param_annotation = get_type_hints(_pydantic_model)[field_name]
            field = model_field.field_info
            if not isinstance(field, BaseField):
                continue
            if isinstance(field, BaseField) and field.alias:
                field_name = field.alias
            http_param_type: HttpParamTypeLiteral = field.get_field_name()  # type: ignore
            if http_param_type not in http_param_type_annotation_dict:
                http_param_type_annotation_dict[http_param_type] = {}
            http_param_type_annotation_dict[http_param_type][field_name] = (param_annotation, field)
            param_field_dict[http_param_type] = field

        for http_param_type, annotation_dict in http_param_type_annotation_dict.items():
            if http_param_type not in http_param_type_dict:
                http_param_type_dict[http_param_type] = []
            http_param_type_dict[http_param_type].append(
                RequestModel(
                    description="",
                    media_type_list=[param_field_dict[http_param_type].media_type],
                    openapi_serialization=param_field_dict[http_param_type].openapi_serialization,
                    model=create_pydantic_model(annotation_dict, class_name=_pydantic_model.__name__),
                )
            )

    def parameter_list_handle(
        self,
        parameter_list: List["inspect.Parameter"],
        http_param_type_dict: HttpParamTypeDictType,
        single_field_list: List[Tuple[str, "inspect.Parameter"]],
        pait_model: PaitCoreModel,
    ) -> None:
        """parse parameter_list to field_dict and single_field_list"""
        for parameter in parameter_list:
            if parameter.default != parameter.empty:
                annotation: type = parameter.annotation
                pait_field: Union[BaseField, Depends] = parameter.default
                if (
                    inspect.isclass(annotation)
                    and issubclass(annotation, BaseModel)
                    and not isinstance(pait_field, Depends)
                ):
                    # support def test(pait_model_route: BaseModel = Body())
                    http_param_type: HttpParamTypeLiteral = pait_field.get_field_name()  # type: ignore
                    required: bool = True
                    if pait_field.default is not Undefined:
                        required = True
                    elif pait_field.default_factory is not None:
                        required = True

                    request_model: RequestModel = RequestModel(
                        description=annotation.__doc__ or "",
                        required=required,
                        media_type_list=[pait_field.media_type],
                        openapi_serialization=pait_field.openapi_serialization,
                        # support raw_return is True
                        model=create_pydantic_model(
                            {parameter.name: (parameter.annotation, Field)},
                            class_name=(
                                f"{pait_model.func_name.title()}{parameter.name.title()}{pait_model.pait_id.title()}"
                            ),
                        )
                        if not pait_field.raw_return
                        else annotation,
                    )
                    if http_param_type not in http_param_type_dict:
                        http_param_type_dict[http_param_type] = []
                    http_param_type_dict[http_param_type].append(request_model)
                else:
                    # def test(pait_model_route: int = Body())
                    if isinstance(pait_field, Depends):
                        http_param_type_dict.update(
                            self._parse_func_param_to_http_param_type_dict(pait_field.func, pait_model)
                        )
                    else:
                        field_name: str = pait_field.__class__.__name__.lower()
                        single_field_list.append((field_name, parameter))

            elif inspect.isclass(parameter.annotation) and issubclass(parameter.annotation, BaseModel):
                # def test(pait_model_route: PaitBaseModel)
                self._parse_base_model_to_http_param_type_dict(http_param_type_dict, parameter.annotation)

    def _parse_func_param_to_http_param_type_dict(
        self, func: Callable, pait_model: PaitCoreModel
    ) -> HttpParamTypeDictType:
        http_param_type_dict: HttpParamTypeDictType = {}
        func_sig: FuncSig = get_func_sig(func)
        single_field_list: List[Tuple[str, "inspect.Parameter"]] = []

        qualname: str = getattr(func, "__qualname__", "")
        if not qualname:
            class_ = func.__class__  # type: ignore
        else:
            qualname = qualname.split(".<locals>", 1)[0].rsplit(".", 1)[0]
            class_ = getattr(inspect.getmodule(func), qualname)

        if inspect.isclass(class_):
            parameter_list: List["inspect.Parameter"] = get_parameter_list_from_class(class_)
            self.parameter_list_handle(parameter_list, http_param_type_dict, single_field_list, pait_model)
        self.parameter_list_handle(func_sig.param_list, http_param_type_dict, single_field_list, pait_model)

        if single_field_list:
            annotation_dict: Dict[str, Tuple[Type, Any]] = {}
            _column_name_set: Set[str] = set()
            for field_name, parameter in single_field_list:
                field: BaseField = parameter.default
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
                            f"{pait_model.func_name.title()}{parameter.name.title()}{pait_model.pait_id.title()}"
                        ),
                    )
                    self._parse_base_model_to_http_param_type_dict(http_param_type_dict, _pydantic_model)
                else:
                    _column_name_set.add(key)
                    annotation_dict[parameter.name] = (parameter.annotation, field)

            _pydantic_model = create_pydantic_model(
                annotation_dict, class_name=f"{pait_model.func_name.title()}{pait_model.pait_id.title()}"
            )
            self._parse_base_model_to_http_param_type_dict(http_param_type_dict, _pydantic_model)

        for extra_openapi_model in pait_model.extra_openapi_model_list:
            self._parse_base_model_to_http_param_type_dict(http_param_type_dict, extra_openapi_model)
        return http_param_type_dict

    def _parse_pait_model_to_http_param_type_dict(self, pait_model: PaitCoreModel) -> HttpParamTypeDictType:
        """Extracting request and response information through routing functions"""
        http_param_type_dict: HttpParamTypeDictType = self._parse_func_param_to_http_param_type_dict(
            pait_model.func, pait_model
        )
        for pre_depend in pait_model.pre_depend_list:
            for http_param_type, request_model_list in self._parse_func_param_to_http_param_type_dict(
                pre_depend, pait_model
            ).items():
                if http_param_type not in http_param_type_dict:
                    http_param_type_dict[http_param_type] = request_model_list
                else:
                    http_param_type_dict[http_param_type].extend(request_model_list)
        return http_param_type_dict
