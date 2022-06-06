from typing import Optional


def get_redoc_html(
    open_api_json_url: str,
    src_url: Optional[str] = None,
    title: str = "ReDoc",
) -> str:
    """copy from https://github.com/Redocly/redoc#tldr"""
    if not src_url:
        src_url = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>{title}</title>
        <!-- needed for adaptive design -->
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

        <!--
        ReDoc doesn't change outer page styles
        -->
        <style>
          body {{
            margin: 0;
            padding: 0;
          }}
        </style>
      </head>
      <body>
        <redoc spec-url='{open_api_json_url}'></redoc>
        <script src={src_url}> </script>
      </body>
    </html>
    """


def get_swagger_ui_html(
    open_api_json_url: str,
    title: str = "Swagger",
    swagger_ui_url: Optional[str] = None,
    swagger_ui_bundle: Optional[str] = None,
    swagger_ui_standalone_preset: Optional[str] = None,
) -> str:
    if not swagger_ui_url:
        swagger_ui_url = "https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css"
    if not swagger_ui_bundle:
        swagger_ui_bundle = "https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js"
    if not swagger_ui_standalone_preset:
        swagger_ui_standalone_preset = "https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-standalone-preset.js"

    return f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta
      name="description"
      content="SwaggerUI"
    />
    <title>{title}</title>
    <link rel="stylesheet" href="{swagger_ui_bundle}" />
  </head>
  <body>
  <div id="swagger-ui"></div>
  <script src="{swagger_ui_bundle}" crossorigin></script>
  <script src="{swagger_ui_standalone_preset}" crossorigin></script>
  <script>
    window.onload = () => {{
      window.ui = SwaggerUIBundle({{
        url: '{open_api_json_url}',
        dom_id: '#swagger-ui',
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        layout: "StandaloneLayout",
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true
      }});
    }};
  </script>
  </body>
</html>
"""
    # return f"""
    # <!DOCTYPE html>
    # <html>
    # <head>
    # <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
    # <link rel="shortcut icon" href="https://static1.smartbear.co/swagger/media/assets/swagger_fav.png">
    # <title>{title}</title>
    # </head>
    # <body>
    # <div id="swagger-ui">
    # </div>
    # <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
    # <!-- `SwaggerUIBundle` is now available on the page -->
    # <script>
    # const ui = SwaggerUIBundle({{
    #     url: '{open_api_json_url}',
    #     dom_id: '#swagger-ui',
    #     presets: [
    #     SwaggerUIBundle.presets.apis,
    #     SwaggerUIBundle.SwaggerUIStandalonePreset
    #     ],
    #     layout: "BaseLayout",
    #     deepLinking: true,
    #     showExtensions: true,
    #     showCommonExtensions: true
    # }})
    # </script>
    # </body>
    # </html>
    # """
