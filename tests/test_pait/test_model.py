import json
from datetime import datetime
from decimal import Decimal
from typing import Type, Union

import pytest
from pydantic import BaseModel, Field

from example.common.request_model import SexEnum
from pait.model import response, tag
from pait.model.config import Config
from pait.openapi.openapi import LinksModel


class TestConfigModel:
    def test_repeat_config_init(self) -> None:
        config: Config = Config()
        config.author = "so1n"  # type: ignore
        assert config.author == "so1n"
        assert not config.initialized
        config.init_config()
        assert config.initialized

        with pytest.raises(RuntimeError) as e:
            config.init_config()

        exec_msg: str = e.value.args[0]
        assert "Can not set new value in runtime" in exec_msg
        with pytest.raises(RuntimeError) as e:
            config.author = "test"  # type: ignore

        exec_msg = e.value.args[0]
        assert "Can not set new value in runtime" in exec_msg

    def test_default_json_encoder(self) -> None:
        config: Config = Config()
        assert json.dumps(
            {
                "date": datetime.fromtimestamp(0).date(),
                "datetime": datetime.fromtimestamp(1600000000),
                "decimal": Decimal("0.0"),
                "enum": SexEnum.man,
                "int": 1,
                "str": "",
            },
            cls=config.json_encoder,
        ) == json.dumps(
            {"date": "1970-01-01", "datetime": 1600000000, "decimal": 0.0, "enum": "man", "int": 1, "str": ""}
        )


class TestLinksModel:
    def test_links_model(self) -> None:
        class DemoResponseModel(response.BaseResponseModel):
            response_data = ""

        # not found header
        with pytest.raises(KeyError) as e:
            LinksModel(DemoResponseModel, "$response.header.")._check_openapi_runtime_expr()

        exec_msg: str = e.value.args[0]
        assert "Can not found header key" in exec_msg

        # not base model response data
        with pytest.raises(RuntimeError) as e:  # type: ignore
            LinksModel(DemoResponseModel, "$response.body#")._check_openapi_runtime_expr()

        exec_msg = e.value.args[0]
        assert "response_data type is pydantic.Basemodel" in exec_msg

        # not support expr
        with pytest.raises(ValueError) as e:  # type: ignore
            LinksModel(DemoResponseModel, "$response.body")._check_openapi_runtime_expr()

        exec_msg = e.value.args[0]
        assert "Only support $response.headerXXX or $response.bodyXXX. " in exec_msg


class TestTagModel:
    def test_repeat_register_tag(self) -> None:
        tag.Tag("TestDemo", "test create tag")
        tag.Tag("TestDemo", "test create tag")

        with pytest.raises(KeyError):
            tag.Tag("TestDemo", "test create tag by other desc")


class TestResponseModel:
    def _test_dict_response_model(
        self, parent_response_class: Union[Type[response.JsonResponseModel], Type[response.XmlResponseModel]]
    ) -> None:
        def factory_value() -> str:
            return "mock"

        class DemoResponseModel(parent_response_class):  # type: ignore
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
                sub_data: SubModel

            response_data: Type[BaseModel] = DataModel

        assert DemoResponseModel.get_default_dict() == {
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
        assert DemoResponseModel.get_example_value() == {
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

    def test_json_response_model(self) -> None:
        for i in [response.JsonResponseModel, response.JsonResponseModel]:
            self._test_dict_response_model(i)  # type: ignore

    def test_xml_response_model(self) -> None:
        for i in [response.XmlResponseModel, response.XmlResponseModel]:
            self._test_dict_response_model(i)  # type: ignore
