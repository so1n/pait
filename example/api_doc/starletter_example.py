from pait.api_doc.markdown import PaitMd
from pait.app.starletter import load_app

from example.param_verify.starletter_example import app

load_app(app)
PaitMd(use_html_details=False).gen_markdown_text()
