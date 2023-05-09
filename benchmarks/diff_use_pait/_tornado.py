from tornado.web import Application, RequestHandler

from benchmarks.common import RequestDataModel
from pait import field
from pait.app.tornado import pait

token_db_dict: dict = {}


def get_user_id_by_token(token: str = field.Header.t()) -> str:
    return token_db_dict.get(token, "")


class UserInfoByPaitHandler(RequestHandler):
    @pait()
    async def get(
        self,
        uid: str = field.Depends.t(get_user_id_by_token),
        name: str = field.Query.t(),
        age: int = field.Query.t(),
        sex: str = field.Query.t(),
    ) -> None:
        self.write(
            {
                "uid": uid,
                "name": name,
                "age": age,
                "sex": sex,
            }
        )


class UserInfoHandler(RequestHandler):
    async def get(self) -> None:
        request_dict = {key: value[0].decode() for key, value in self.request.query_arguments.items()}
        self.write(
            RequestDataModel(
                uid=token_db_dict.get(self.request.headers.get("token", ""), ""),
                name=request_dict.get("name", ""),
                age=int(request_dict.get("age", 0)),
                sex=request_dict.get("sex", ""),
            ).dict()
        )


def create_app() -> Application:
    app: Application = Application(
        [
            (r"/api/user-info-by-pait", UserInfoByPaitHandler),
            (r"/api/user-info", UserInfoHandler),
        ]
    )
    return app
