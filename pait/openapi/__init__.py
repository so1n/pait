# from pydantic import BaseModel, Field, version, create_model
#
# class Faker(object):
#     pass
#
#
# aaa = create_model(
#     "Demoaaa",
#     aaa = (str, Field(links=Faker()))
# )
# print(aaa.model_fields)
# aaa.model_fields['aaa'].json_schema_extra.pop('links')
# print(aaa.model_fields)
# print(aaa.model_json_schema())
#
#
# class Demo(BaseModel):
#     aaa: int = Field(links=Faker())
#
# print(version.VERSION)
# Demo.model_fields["aaa"].json_schema_extra.pop("links")
# print(Demo.model_json_schema())


#
# aaa = {}
# bbb = {"a": 1, "b": 2}
# ccc = {}
#
# def _handle(v):
#     global ccc
#     v.update(bbb)
#     ccc = v
#
# print(id(aaa), id(bbb), id(ccc))
# _handle(aaa)
# print(aaa)
# aaa.pop("a")
# print(ccc)
# print(id(aaa), id(bbb), id(ccc))
