import importlib
from typing import Dict

from pait.app.auto_load_app import app_list
from pait.core import PaitCoreModel


class TestApiDoc:
    """Now, ignore test api doc"""

    def test_app_api_doc(self) -> None:
        for app_name in app_list:
            module = importlib.import_module(f"example.api_doc.{app_name}_example")  # type: ignore
            pait_dict: Dict[str, PaitCoreModel] = module.load_app(module.create_app(), project_name="")  # type: ignore

            module.PaitMd(pait_dict, use_html_details=True)  # type: ignore
            for i in ("json", "yaml"):
                module.PaitOpenApi(  # type: ignore
                    pait_dict,
                    title="Pait Doc",
                    open_api_tag_list=[
                        {"name": "test", "description": "test api"},
                        {"name": "user", "description": "user api"},
                    ],
                    type_=i,
                )
