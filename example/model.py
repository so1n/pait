from pydantic import (
    BaseModel,
    conint,
    constr,
)


class UserModel(BaseModel):
    uid: conint(gt=10, lt=1000)
    user_name: constr(min_length=2, max_length=4)


class UserOtherModel(BaseModel):
    age: conint(gt=1, lt=100)
