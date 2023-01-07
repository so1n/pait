from typing import Dict

from any_api.openapi.to.markdown import Markdown

from example.api_doc.utils import my_serialization
from example.param_verify.tornado_example import create_app
from pait.api_doc.openapi import OpenAPI
from pait.app import load_app
from pait.extra.config import apply_block_http_method_set
from pait.g import config
from pait.model.core import PaitCoreModel

if __name__ == "__main__":
    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    pait_dict: Dict[str, PaitCoreModel] = load_app(create_app())

    print(OpenAPI(pait_dict).content())
    print(OpenAPI(pait_dict).content(serialization_callback=my_serialization))
    for i18n_lang in ("zh-cn", "en"):
        print(Markdown(OpenAPI(pait_dict), i18n_lang=i18n_lang).content)
