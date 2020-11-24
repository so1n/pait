from pait.api_doc.markdown import PaitMd
from pait.app import load_app

from example.param_verify.starletter_example import app

load_app(app)
PaitMd(use_html_details=False, output_file='starletter_pait.md').gen_markdown_text()

