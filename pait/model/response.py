from typing import Any, Dict, Optional, Tuple, Type, Union

from pydantic import BaseModel

from pait.util import gen_example_dict_from_pydantic_base_model


class PaitBaseResponseModel(object):
    """response model https://swagger.io/docs/specification/describing-responses/"""

    # Used for mock response and response checking to determine if the response model is the core response model
    is_core: bool = False

    # response data
    response_data: Union[Type[BaseModel], str, bytes]
    # response media type
    media_type: str

    # response name
    name: Optional[str] = None
    # response description
    description: Optional[str] = None
    # response header
    header: dict = {}
    # response status code
    status_code: Tuple[int] = (200,)

    # The value of this response in openapi.schema
    # if value is empty, pait will auto gen response model and set to openapi.schema
    openapi_schema: Optional[dict] = None

    # links model
    links_schema_dict: Dict[str, dict] = {}

    @classmethod
    def is_base_model_response_data(cls) -> bool:
        return isinstance(cls.response_data, type) and issubclass(cls.response_data, BaseModel)

    @classmethod
    def get_example_value(cls, **extra: Any) -> Any:
        return cls.response_data

    @classmethod
    def register_link_schema(cls, link_schema: dict) -> None:
        cls.links_schema_dict.update(link_schema)


class PaitJsonResponseModel(PaitBaseResponseModel):
    response_data: Type[BaseModel]
    media_type: str = "application/json"

    @classmethod
    def get_example_value(cls, **extra: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(cls.response_data)

    @classmethod
    def get_default_dict(cls, **extra: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(cls.response_data, use_example_value=False)


class PaitResponseModel(PaitJsonResponseModel):
    """
    PaitJsonResponseModel alias
    Compatible versions below 0.7
    """


class PaitTextResponseModel(PaitBaseResponseModel):
    response_data: str = "pait example data"
    media_type: str = "text/plain"

    openapi_schema: dict = {"type": "string", "example": response_data}


class PaitHtmlResponseModel(PaitBaseResponseModel):
    response_data: str = "<h1>Pait example html</h1>"
    media_type: str = "text/html"

    openapi_schema: dict = {"type": "string", "example": response_data}


class PaitFileResponseModel(PaitBaseResponseModel):
    response_data: bytes = b"pait example bytes"
    media_type: str = "application/octet-stream"

    openapi_schema: dict = {"type": "string", "format": "binary"}
