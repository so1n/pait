from typing import Optional, Tuple, Type

from pydantic import BaseModel


class PaitResponseModel(object):
    """response model"""

    # response name
    name: Optional[str] = None
    # response description
    description: Optional[str] = None
    # response header
    header: dict = {}
    # response media type
    media_type: str = "application/json"
    # response data
    response_data: Optional[Type[BaseModel]] = None
    # response status code
    status_code: Tuple[int] = (200,)
