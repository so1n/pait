from typing import Dict

from example.param_verify.tornado_example import create_app
from pait.api_doc.markdown import PaitMd
from pait.api_doc.open_api import PaitOpenApi
from pait.api_doc.pait_json import PaitJson
from pait.api_doc.pait_yaml import PaitYaml
from pait.app import load_app
from pait.model import PaitCoreModel

if __name__ == "__main__":
    filename: str = "./example_doc/tornado"
    pait_dict: Dict[str, PaitCoreModel] = load_app(create_app())
    PaitMd(pait_dict, use_html_details=True, filename=filename)
    PaitJson(pait_dict, filename=filename, indent=2)
    PaitYaml(pait_dict, filename=filename)

    for i in ("json", "yaml"):
        PaitOpenApi(
            pait_dict,
            title="Pait Doc",
            open_api_tag_list=[
                {"name": "test", "description": "test api"},
                {"name": "user", "description": "user api"},
            ],
            type_=i,
            filename=filename + "_openapi",
        )