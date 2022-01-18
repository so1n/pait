from typing import TYPE_CHECKING, List, Type

from pydantic import BaseModel

if TYPE_CHECKING:
    from pait import field

    from .core import PaitCoreModel
    from .response import PaitBaseResponseModel


class LinksModel(object):
    param_name: str
    pait_field: "field.BaseField"
    link_name: str
    operation_id: str
    parameters_dict: dict

    def __init__(self, pait_response_model: "Type[PaitBaseResponseModel]", openapi_runtime_expr: str, desc: str = ""):
        """
        doc: https://swagger.io/docs/specification/links/
        :param pait_response_model: pait response model
        :param openapi_runtime_expr: open api runtime expression syntax.
            Only support $response.headerXXX or $response.bodyXXX
            Please refer to the section of the document at `Runtime Expression Syntax`
        :param desc: links desc
        """
        self.openapi_runtime_expr: str = openapi_runtime_expr
        self.pait_response_model: "Type[PaitBaseResponseModel]" = pait_response_model
        self.desc: str = desc
        self._cache: dict = {}

    def _check_openapi_runtime_expr(self) -> None:
        if self.openapi_runtime_expr.startswith("$response.header."):
            header_key: str = self.openapi_runtime_expr.replace("$response.header.", "")
            if header_key not in self.pait_response_model.header:
                raise KeyError(f"Can not found header key:{header_key} from {self.pait_response_model}")
        elif self.openapi_runtime_expr.startswith("$response.body#"):
            if not self.pait_response_model.is_base_model_response_data():
                raise RuntimeError(
                    f"Expr: {self.openapi_runtime_expr} only support "
                    f"pait_response_model.response_data type is pydantic.Basemodel"
                )
            try:
                key_list: List[str] = [
                    i for i in self.openapi_runtime_expr.replace("$response.body#", "").split("/") if i
                ]
            except Exception:
                raise RuntimeError(
                    f"Check expr: {self.openapi_runtime_expr} error."
                    "Please refer to the section of the document(https://swagger.io/docs/specification/links/) "
                    "at `Runtime Expression Syntax`"
                )  # pragma: no cover

            base_model: Type[BaseModel] = self.pait_response_model.response_data  # type: ignore
            for key in key_list:
                if key not in base_model.__fields__:
                    raise ValueError(
                        f"check expr:{self.openapi_runtime_expr} error "  # type: ignore
                        f"from {self.pait_response_model.response_data}"  # type: ignore
                    )
                temp_type: Type = base_model.__fields__[key].type_
                if issubclass(temp_type, BaseModel):
                    base_model = temp_type
        else:
            raise ValueError(
                "Only support $response.headerXXX or $response.bodyXXX. "
                "Please refer to the section of the document(https://swagger.io/docs/specification/links/) "
                "at `Runtime Expression Syntax`"
            )

    def register(self, pait_model: "PaitCoreModel", param_name: str, pait_field: "field.BaseField") -> None:
        """
        In order not to affect the startup speed, this method is only allowed to be called under the openapi module"""
        param_name = pait_field.alias or param_name
        for method in pait_model.method_list:
            operation_id: str = f"{method}.{pait_model.operation_id}"
            global_key: str = f"{operation_id}/{pait_field.get_field_name()}/{param_name}"
            if global_key in self._cache:
                return

            self._check_openapi_runtime_expr()
            self.pait_response_model.register_link_schema(
                {
                    global_key: {
                        "description": self.desc,
                        "operationId": operation_id,
                        "parameters": {param_name: self.openapi_runtime_expr},
                    }
                }
            )
