import importlib
from typing import Dict

from pait.app.auto_load_app import app_list
from pait.model import PaitCoreModel


class TestApiDoc:
    """Now, ignore test api doc"""

    def test_app_api_doc(self) -> None:
        from example.common.utils import my_serialization
        from pait.openapi.openapi import OpenAPI

        for app_name in app_list:
            module = importlib.import_module(f"example.{app_name}_example.main_example")  # type: ignore
            pait_dict: Dict[str, PaitCoreModel] = module.load_app(module.create_app())  # type: ignore

            OpenAPI(pait_dict).content()  # type: ignore
            OpenAPI(pait_dict).content(serialization_callback=my_serialization)  # type: ignore
