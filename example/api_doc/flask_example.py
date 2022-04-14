from typing import Dict

from example.param_verify.flask_example import create_app
from pait.api_doc.markdown import PaitMd
from pait.api_doc.open_api import PaitOpenAPI
from pait.app import load_app
from pait.extra.config import apply_block_http_method_set
from pait.g import config
from pait.model.core import PaitCoreModel
from pait.util import I18nContext

if __name__ == "__main__":
    filename: str = "./example_doc/flask_pait"
    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    pait_dict: Dict[str, PaitCoreModel] = load_app(create_app())
    for i18n_lang in ("zh-cn", "en"):
        with I18nContext(i18n_lang):
            PaitMd(pait_dict, use_html_details=True).output(f"{filename}-{i18n_lang}")
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
