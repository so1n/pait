from typing import Any, Dict, List, Optional

from example.common import tag
from example.common.request_model import SexEnum, TestPaitModel, UserModel, UserOtherModel
from example.common.response_model import FailRespModel, SimpleRespModel, UserSuccessRespModel
from example.tornado_example.utils import MyHandler, global_pait
from pait.app.tornado import Pait
from pait.field import Cookie, File, Form, Header, Json, MultiForm, MultiQuery, Path, Query
from pait.model.status import PaitStatus

field_pait: Pait = global_pait.create_sub_pait(
    group="field",
    status=PaitStatus.release,
    tag=(tag.field_tag,),
)


class PostHandler(MyHandler):
    @field_pait(
        append_tag=(tag.user_tag, tag.post_tag),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(
        self,
        model: UserModel = Json.i(raw_return=True),
        other_model: UserOtherModel = Json.i(raw_return=True),
        sex: SexEnum = Json.i(description="sex"),
        content_type: str = Header.i(alias="Content-Type", description="content-type"),
    ) -> None:
        """Test Method:Post Pydantic Model"""
        return_dict = model.dict()
        return_dict["sex"] = sex.value
        return_dict.update(other_model.dict())
        return_dict.update({"content_type": content_type})
        self.write({"code": 0, "msg": "", "data": return_dict})


class SameAliasHandler(MyHandler):
    @field_pait(
        tag=(tag.same_alias_tag,),
        response_model_list=[SimpleRespModel, FailRespModel],
    )
    def get(
        self, query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
    ) -> None:
        self.write({"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}})


class FieldDefaultFactoryHandler(MyHandler):
    @field_pait(
        response_model_list=[SimpleRespModel, FailRespModel],
    )
    async def post(
        self,
        demo_value: int = Json.i(description="Json body value not empty"),
        data_list: List[str] = Json.i(default_factory=list, description="test default factory"),
        data_dict: Dict[str, Any] = Json.i(default_factory=dict, description="test default factory"),
    ) -> None:
        self.write(
            {"code": 0, "msg": "", "data": {"demo_value": demo_value, "data_list": data_list, "data_dict": data_dict}}
        )


class PaitBaseFieldHandler(MyHandler):
    @field_pait(
        response_model_list=[SimpleRespModel, FailRespModel],
    )
    async def post(
        self,
        upload_file: Dict = File.i(raw_return=True, description="upload file"),
        a: str = Form.i(description="form data"),
        b: str = Form.i(description="form data"),
        c: List[str] = MultiForm.i(description="form data"),
        cookie: dict = Cookie.i(raw_return=True, description="cookie"),
        multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
        age: int = Path.i(description="age", gt=1, lt=100),
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
        sex: SexEnum = Query.i(description="sex"),
    ) -> None:
        self.write(
            {
                "code": 0,
                "msg": "",
                "data": {
                    "filename": list(upload_file.values())[0]["filename"],
                    "content": list(upload_file.values())[0]["body"].decode(),
                    "form_a": a,
                    "form_b": b,
                    "form_c": c,
                    "cookie": {key: key for key, _ in cookie.items()},
                    "multi_user_name": multi_user_name,
                    "age": age,
                    "uid": uid,
                    "user_name": user_name,
                    "email": email,
                    "sex": sex,
                },
            }
        )


class PaitModelHanler(MyHandler):
    @field_pait(status=PaitStatus.test, response_model_list=[SimpleRespModel, FailRespModel])
    async def post(self, test_model: TestPaitModel) -> None:
        """Test pait model"""
        self.write({"code": 0, "msg": "", "data": test_model.dict()})


if __name__ == "__main__":
    from tornado.ioloop import IOLoop
    from tornado.web import Application

    from pait.app.tornado import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Application = Application(
        [
            (r"/api/post", PostHandler),
            (r"/api/pait-base-field/(?P<age>\w+)", PaitBaseFieldHandler),
            (r"/api/field-default-factory", FieldDefaultFactoryHandler),
            (r"/api/same-alias", SameAliasHandler),
            (r"/api/pait-model", PaitModelHanler),
        ]
    )
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    app.listen(8000)
    IOLoop.instance().start()
