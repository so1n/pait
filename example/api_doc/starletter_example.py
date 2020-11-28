from pait.api_doc.markdown import PaitMd
from pait.api_doc.pait_json import PaitJson
from pait.api_doc.pait_yaml import PaitYaml
from pait.api_doc.open_api_json import PaitOpenApiJson
from pait.app import load_app

from example.param_verify.starletter_example import app

title: str = 'starletter'
load_app(app)
PaitMd(use_html_details=False, filename=title)
PaitJson(filename=title, indent=2)
PaitYaml(filename=title)
PaitOpenApiJson(filename=title + '_openapi')

