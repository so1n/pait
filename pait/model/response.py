from typing import Optional, Tuple, Type

from pydantic import BaseModel


class PaitResponseModel(object):
    """response model"""

    description: Optional[str] = None
    header: dict = {}
    media_type: str = "application/json"
    response_data: Optional[Type[BaseModel]] = None
    status_code: Tuple[int] = (200,)

    name: Optional[str] = None
