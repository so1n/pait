from pait.api_doc.markdown import PaitMd
from pait.api_doc.pait_json import PaitJson
from pait.app import load_app

from example.param_verify.flask_example import app

load_app(app)
PaitMd(use_html_details=False, output_file='flask_pait.md').gen_markdown_text()
PaitJson(output_file='flask_pait.json', indent=2)
