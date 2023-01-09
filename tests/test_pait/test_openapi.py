import importlib
from typing import Dict

from pait.app.auto_load_app import app_list
from pait.model.core import PaitCoreModel


class TestApiDoc:
    """Now, ignore test api doc"""

    def test_app_api_doc(self) -> None:
        for app_name in app_list:
            module = importlib.import_module(f"example.openapi.{app_name}_example")  # type: ignore
            pait_dict: Dict[str, PaitCoreModel] = module.load_app(module.create_app(), project_name="")  # type: ignore
            module.OpenAPI(pait_dict).content()  # type: ignore
            module.OpenAPI(pait_dict).content(serialization_callback=module.my_serialization)  # type: ignore
