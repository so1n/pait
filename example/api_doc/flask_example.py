from pait.api_doc.markdown import PaitMd
from pait.app.flask import load_app

from example.param_verify.flask_example import app

load_app(app)
PaitMd().gen_markdown_text()
