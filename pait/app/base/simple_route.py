from typing import Callable, List

from pydantic import BaseModel


class SimpleRoute(BaseModel):
    methods: List[str]
    route: Callable
    url: str
