import importlib
from typing import Dict

import pytest
from pydantic import BaseModel, Field

from pait import _pydanitc_adapter, field
from pait.app.auto_load_app import app_list
from pait.app.base import BaseAppHelper
from pait.app.base.security.api_key import BaseAPIKey
from pait.model.core import PaitCoreModel
from pait.openapi.openapi import HttpParamTypeLiteral, ParsePaitModel
from pait.param_handle import ParamHandler


class TestParsePaitModel:
    @staticmethod
    def check_result_by_http_param_type_dict(
        parse_pait_model: ParsePaitModel, field_http_param_type_dict: Dict[str, HttpParamTypeLiteral]
    ) -> None:
        for field_name, http_param_type in field_http_param_type_dict.items():
            assert len(parse_pait_model.http_param_type_dict[http_param_type]) == 1
            assert (
                len(_pydanitc_adapter.model_fields(parse_pait_model.http_param_type_dict[http_param_type][0].model))
                == 1
            )
            assert field_name in _pydanitc_adapter.model_fields(
                parse_pait_model.http_param_type_dict[http_param_type][0].model
            )

    def test_extra_openapi_model(self) -> None:
        def demo() -> None:
            pass

        class ExtraModel(BaseModel):
            a: int = field.Query.i()
            b: str = field.Body.i()
            c: str = field.File.i()

        core_model = PaitCoreModel(demo, BaseAppHelper, ParamHandler)
        core_model.extra_openapi_model_list.append(ExtraModel)
        parse_pait_model = ParsePaitModel(core_model)
        self.check_result_by_http_param_type_dict(parse_pait_model, {"a": "query", "b": "body", "c": "file"})

    def test_pre_depend_list(self) -> None:
        def demo() -> None:
            pass

        def demo_depend(
            a: int = field.Query.i(),
            b: str = field.Body.i(),
            c: str = field.File.i(),
        ) -> None:
            pass

        core_model = PaitCoreModel(demo, BaseAppHelper, ParamHandler, pre_depend_list=[demo_depend])
        parse_pait_model = ParsePaitModel(core_model)
        self.check_result_by_http_param_type_dict(parse_pait_model, {"a": "query", "b": "body", "c": "file"})

    def test_func(self) -> None:
        def demo(
            a: int = field.Query.i(),
            b: str = field.Body.i(),
            c: str = field.File.i(),
        ) -> None:
            pass

        core_model = PaitCoreModel(demo, BaseAppHelper, ParamHandler)
        parse_pait_model = ParsePaitModel(core_model)
        self.check_result_by_http_param_type_dict(parse_pait_model, {"a": "query", "b": "body", "c": "file"})

    def test_parse_base_model(self) -> None:
        def demo() -> None:
            pass

        core_model = PaitCoreModel(demo, BaseAppHelper, ParamHandler, default_field_class=field.File)
        parse_pait_model = ParsePaitModel(core_model)

        class ExtraModel(BaseModel):
            a: int = field.Query.i()
            bb: str = field.Body.i(alias="b")
            c: str = Field()
            d: int = field.Query.i(openapi_include=False)

        parse_pait_model._parse_base_model(ExtraModel)
        parse_pait_model.build()
        self.check_result_by_http_param_type_dict(parse_pait_model, {"a": "query", "b": "body", "c": "file"})

    def test_func_type_is_base_model(self) -> None:
        class Demo(BaseModel):
            a: int = Field()
            b: str = Field()

        def demo(aaa: Demo = field.Query.i()) -> None:
            pass

        core_model = PaitCoreModel(demo, BaseAppHelper, ParamHandler)
        parse_pait_model = ParsePaitModel(core_model)
        self.check_result_by_http_param_type_dict(parse_pait_model, {"aaa": "query"})

        def demo1(aaa: Demo = field.Query.i(raw_return=True)) -> None:
            pass

        core_model = PaitCoreModel(demo1, BaseAppHelper, ParamHandler)
        parse_pait_model = ParsePaitModel(core_model)
        assert len(parse_pait_model.http_param_type_dict["query"]) == 1
        assert len(_pydanitc_adapter.model_fields(parse_pait_model.http_param_type_dict["query"][0].model)) == 2
        assert {"a", "b"} == {
            k for k in _pydanitc_adapter.model_fields(parse_pait_model.http_param_type_dict["query"][0].model).keys()
        }

    def test_same_security(self) -> None:
        def demo(
            api_key_1: str = field.Depends.t(BaseAPIKey(name="demo1", field=field.Header.i(), security_name="demo")),
            api_key_2: str = field.Depends.t(BaseAPIKey(name="demo2", field=field.Header.i(), security_name="demo")),
        ) -> None:
            pass

        core_model = PaitCoreModel(demo, BaseAppHelper, ParamHandler)

        with pytest.raises(ValueError):
            ParsePaitModel(core_model)


class TestApiDoc:
    """Now, ignore test api doc"""

    def test_app_api_doc(self) -> None:
        from example.common.utils import my_serialization
        from pait.openapi.openapi import OpenAPI

        for app_name in app_list:
            module = importlib.import_module(f"example.{app_name}_example.main_example")  # type: ignore
            app = module.create_app()  # type: ignore

            OpenAPI(app).content()  # type: ignore
            OpenAPI(app).content(serialization_callback=my_serialization)  # type: ignore
            OpenAPI(app).dict  # type: ignore
