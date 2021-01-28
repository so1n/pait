from pait.api_doc.markdown import PaitMd
from pait.api_doc.pait_json import PaitJson
from pait.api_doc.pait_yaml import PaitYaml
from pait.api_doc.open_api import PaitOpenApi
from pait.app import load_app

from example.param_verify.flask_example import app

title: str = 'flask_pait'
load_app(app)
PaitMd(use_html_details=False, filename=title)
PaitJson(filename=title, indent=2)
PaitYaml(filename=title)
PaitOpenApi(filename=title + '_openapi')
