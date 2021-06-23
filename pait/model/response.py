from dataclasses import dataclass, field
from typing import List, Optional, Type

from pydantic import BaseModel


@dataclass()
class PaitResponseModel(object):
    """response model"""

    description: Optional[str] = ""
    header: dict = field(default_factory=dict)
    media_type: str = "application/json"
    response_data: Optional[Type[BaseModel]] = None
    status_code: List[int] = field(default_factory=lambda: [200])

    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.__class__.__name__
