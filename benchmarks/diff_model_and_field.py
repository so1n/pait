from pydantic import Field
from pydantic.config import BaseConfig
from pydantic.fields import ModelField

from benchmarks.diff_use_pait.run import run_and_calculate_time
from pait.util import create_pydantic_model


def create_pydantic_model_demo() -> dict:
    return create_pydantic_model(
        {
            "uid": (str, Field(...)),
            "name": (str, Field(...)),
            "age": (int, Field(...)),
            "sex": (str, Field(...)),
        }
    )(uid="10086", name="John Doe", age="32", sex="M").dict()


def create_pydantic_field_demo() -> dict:
    temp_dict: dict = {}
    uid, _ = ModelField(
        name="uid", type_=str, field_info=Field(...), class_validators={}, model_config=BaseConfig
    ).validate("10086", temp_dict, loc="demo")
    name, _ = ModelField(
        name="name", type_=str, field_info=Field(...), class_validators={}, model_config=BaseConfig
    ).validate("John Doe", temp_dict, loc="demo")
    age, _ = ModelField(
        name="age", type_=int, field_info=Field(...), class_validators={}, model_config=BaseConfig
    ).validate("32", temp_dict, loc="demo")
    sex, _ = ModelField(
        name="sex", type_=str, field_info=Field(...), class_validators={}, model_config=BaseConfig
    ).validate("M", temp_dict, loc="demo")
    return {"uid": uid, "name": name, "age": age, "sex": sex}


if __name__ == "__main__":
    print("create pydantic model and validate duration:", run_and_calculate_time(create_pydantic_model_demo))
    print("create field and validate duration:", run_and_calculate_time(create_pydantic_field_demo))
