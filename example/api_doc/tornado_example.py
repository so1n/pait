from typing import Dict

from example.param_verify.tornado_example import create_app
from pait.api_doc.markdown import PaitMd
from pait.api_doc.open_api import PaitOpenAPI
from pait.app import load_app
from pait.model.core import PaitCoreModel

if __name__ == "__main__":
    filename: str = "./example_doc/tornado"
    pait_dict: Dict[str, PaitCoreModel] = load_app(create_app())
    for i18n_lang in ("zh-cn", "en"):
        PaitMd(pait_dict, use_html_details=True, i18n_lang=i18n_lang).output(f"{filename}-{i18n_lang}")
    for i in ("json", "yaml"):
        PaitOpenAPI(
            pait_dict,
            title="Pait Doc",
            open_api_tag_list=[
                {"name": "test", "description": "test api"},
                {"name": "user", "description": "user api"},
            ],
            type_=i,
        ).output(filename + "_openapi")
