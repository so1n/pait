from pydantic import BaseModel, Field


class RequestDataModel(BaseModel):
    uid: str = Field(...)
    name: str = Field(...)
    age: int = Field(...)
    sex: str = Field(...)
