from typing import Optional


def get_rapidoc_html(
    open_api_json_url: str,
    title: str = "",
    src_url: Optional[str] = None,
) -> str:
    """
    rapidoc api doc html: https://rapidocweb.com/api.html
    rapidoc example doc html: https://rapidocweb.com/examples.html
    """
    if not src_url:
        src_url = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"
    return f"""
<!doctype html> <!-- Important: must specify -->
<html>
<head>
  <meta charset="utf-8"> <!-- Important: rapi-doc uses utf8 characters -->
  <script type="module" src="{src_url}"></script>
</head>
<body>
  <rapi-doc
    show-info = "true"
    spec-url="{open_api_json_url}"
  > </rapi-doc>
</body>
</html>
"""


def get_rapipdf_html(
    open_api_json_url: str,
    title: str = "",
    src_url: Optional[str] = None,
) -> str:
    if not src_url:
        src_url = "https://unpkg.com/rapipdf/dist/rapipdf-min.js"
    return f"""
  <!doctype html>
  <html>
  <head>
    <script src="{src_url}"></script>
  </head>
  <body>
    <rapi-pdf
      style = "width:700px; height:40px; font-size:18px;"
      spec-url = "{open_api_json_url}"
      button-bg = "#b44646"
    > </rapi-pdf>
  </body>
  </html>
    """
