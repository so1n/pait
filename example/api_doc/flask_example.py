from typing import Dict
from example.param_verify.flask_example import create_app
from pait.api_doc.markdown import PaitMd
from pait.api_doc.open_api import PaitOpenApi
from pait.api_doc.pait_json import PaitJson
from pait.api_doc.pait_yaml import PaitYaml
from pait.app import load_app
from pait.model import PaitCoreModel


if __name__ == "__main__":
    filename: str = "./example_doc/flask_pait"
    pait_dict: Dict[str, PaitCoreModel] = load_app(create_app())
    PaitMd(pait_dict, use_html_details=True, filename=filename)
    PaitJson(pait_dict, filename=filename, indent=2)
    PaitYaml(pait_dict, filename=filename)
    for i in ("json", "yaml"):
        PaitOpenApi(pait_dict, title="Pait Doc", filename=filename + "_openapi", type_=i)
