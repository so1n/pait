from datetime import datetime
from decimal import Decimal
from typing import Type

from pydantic import BaseModel, Field

from example.param_verify.model import SexEnum
from pait.model import response


class TestModelResponse:
    def test_json_response_model(self) -> None:
        def factory_value() -> str:
            return "mock"

        class DemoJsonResponseModel(response.PaitJsonResponseModel):
            class DataModel(BaseModel):
                class SubModel(BaseModel):
                    normal_str_value: str = Field()
                    normal_int_value: int = Field()
                    normal_float_value: float = Field()
                    normal_bool_value: bool = Field()
                    normal_list_value: list = Field()
                    normal_dict_value: dict = Field()
                    normal_tuple_value: tuple = Field()
                    normal_datetime_value: datetime = Field()
                    normal_decimal_value: Decimal = Field()
                    normal_enum_value: SexEnum = Field()

                default_value: str = Field(default="default")
                default_factory_value: str = Field(default_factory=factory_value)
                example_value: str = Field(example="example_value")
                example_factory_value: str = Field(example=factory_value)
                sub_data: "SubModel"

            response_data: Type[BaseModel] = DataModel

        assert DemoJsonResponseModel.get_default_dict() == {
            "default_value": "default",
            "default_factory_value": factory_value(),
            "example_value": "",
            "example_factory_value": "",
            "sub_data": {
                "normal_str_value": "",
                "normal_int_value": 0,
                "normal_float_value": 0.0,
                "normal_bool_value": True,
                "normal_list_value": [],
                "normal_dict_value": {},
                "normal_tuple_value": (),
                "normal_datetime_value": datetime.fromtimestamp(0),
                "normal_decimal_value": Decimal("0.0"),
                "normal_enum_value": SexEnum.man.value,  # type: ignore
            },
        }
        assert DemoJsonResponseModel.get_example_value() == {
            "default_value": "default",
            "default_factory_value": factory_value(),
            "example_value": "example_value",
            "example_factory_value": factory_value(),
            "sub_data": {
                "normal_str_value": "",
                "normal_int_value": 0,
                "normal_float_value": 0.0,
                "normal_bool_value": True,
                "normal_list_value": [],
                "normal_dict_value": {},
                "normal_tuple_value": (),
                "normal_datetime_value": datetime.fromtimestamp(0),
                "normal_decimal_value": Decimal("0.0"),
                "normal_enum_value": SexEnum.man.value,  # type: ignore
            },
        }
