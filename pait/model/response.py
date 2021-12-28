from typing import Optional, Tuple, Type, Union

from pydantic import BaseModel


class PaitBaseResponseModel(object):
    """response model https://swagger.io/docs/specification/describing-responses/"""

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

    @classmethod
    def is_base_model_response_data(cls) -> bool:
        return isinstance(cls.response_data, type) and issubclass(cls.response_data, BaseModel)


class PaitJsonResponseModel(PaitBaseResponseModel):
    response_data: Type[BaseModel]
    media_type: str = "application/json"


class PaitResponseModel(PaitJsonResponseModel):
    """
    PaitJsonResponseModel alias
    Compatible versions below 0.7
    """


class PaitTextResponseModel(PaitBaseResponseModel):
    response_data: str = ""
    media_type: str = "text/plain"

    openapi_schema: dict = {"type": "string", "example": "pong"}


class PaitHtmlResponseModel(PaitBaseResponseModel):
    response_data: str = ""
    media_type: str = "text/html"

    openapi_schema: dict = {"type": "string", "example": "<H1>pong</H1>"}


class PaitFileResponseModel(PaitBaseResponseModel):
    response_data: bytes = b""
    media_type: str = "application/octet-stream"

    openapi_schema: dict = {"type": "string", "format": "binary"}
