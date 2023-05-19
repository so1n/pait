from any_api.openapi.to.markdown import Markdown

from example.common.utils import my_serialization
from example.starlette_example.main_example import create_app
from pait.extra.config import apply_block_http_method_set
from pait.g import config
from pait.openapi.openapi import OpenAPI

if __name__ == "__main__":
    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])
    app = create_app()

    print(OpenAPI(app).content())
    print(OpenAPI(app).content(serialization_callback=my_serialization))
    for i18n_lang in ("zh-cn", "en"):
        print(Markdown(OpenAPI(app), i18n_lang=i18n_lang).content)
