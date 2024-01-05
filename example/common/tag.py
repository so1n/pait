from pait.model.tag import Tag

check_resp_tag: Tag = Tag("check resp", desc="check route response")
check_param_tag: Tag = Tag("check param", desc="check route request param")
links_tag: Tag = Tag("links", desc="openapi links route")
plugin_tag: Tag = Tag("plugin", desc="test pait plugin route")
raise_tag: Tag = Tag("raise", desc="raise route")
user_tag: Tag = Tag("user", desc="user data route")
post_tag: Tag = Tag("post", desc="post method route")
depend_tag: Tag = Tag("depend", desc="depend route")
same_alias_tag: Tag = Tag("same alias", desc="have same alias field route")
field_tag: Tag = Tag("field", desc="field route")
mock_tag: Tag = Tag("mock", desc="mock response route")
cbv_tag: Tag = Tag("cbv", desc="cbv route")
security_tag: Tag = Tag("security", desc="security route")
api_key_tag: Tag = Tag("api-key", desc="api key security route")
oauth2_tag: Tag = Tag("oauth2", desc="oauth2 security route")
http_tag: Tag = Tag("http", desc="http security route")
openapi_exclude_tag = Tag("exclude", openapi_include=False, label="exclude-value")
openapi_include_tag: Tag = Tag("include", desc="demo route", label="include-value")
