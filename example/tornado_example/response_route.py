import time
from typing import Optional

import aiofiles  # type: ignore

from example.common import response_model, tag
from example.tornado_example.utils import MyHandler, create_app, global_pait
from pait.app.tornado import Pait
from pait.field import Query
from pait.model import PaitStatus

check_resp_pait: Pait = global_pait.create_sub_pait(
    group="check_resp", tag=(tag.check_resp_tag,), status=PaitStatus.release
)


class TextResponseHanler(MyHandler):
    @check_resp_pait(response_model_list=[response_model.TextRespModel])
    async def get(self) -> None:
        """test return text response"""
        self.write(str(time.time()))
        self.set_header("X-Example-Type", "text")
        self.set_header("Content-Type", "text/plain")


class HtmlResponseHanler(MyHandler):
    @check_resp_pait(response_model_list=[response_model.HtmlRespModel])
    async def get(self) -> None:
        """test return html response"""
        self.write("<H1>" + str(time.time()) + "</H1>")
        self.set_header("X-Example-Type", "html")
        self.set_header("Content-Type", "text/html")


class FileResponseHanler(MyHandler):
    @check_resp_pait(response_model_list=[response_model.FileRespModel])
    async def get(self) -> None:
        """test return file response"""
        async with aiofiles.tempfile.NamedTemporaryFile() as f:  # type: ignore
            await f.write("Hello Word!".encode())
            await f.seek(0)
            async for line in f:
                self.write(line)

        self.set_header("X-Example-Type", "file")
        self.set_header("Content-Type", "application/octet-stream")


class CheckRespHandler(MyHandler):
    @check_resp_pait(
        append_tag=(tag.user_tag,),
        response_model_list=[response_model.UserSuccessRespModel3, response_model.FailRespModel],
    )
    async def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        age: int = Query.i(description="age", gt=1, lt=100),
        display_age: int = Query.i(0, description="display age"),
    ) -> None:
        """Test test-helper check response"""
        return_dict: dict = {
            "code": 0,
            "msg": "",
            "data": {
                "uid": uid,
                "user_name": user_name,
                "email": email,
            },
        }
        if display_age == 1:
            return_dict["data"]["age"] = age
        self.write(return_dict)


if __name__ == "__main__":
    with create_app() as app:
        app.add_route(
            [
                (r"/api/check-resp", CheckRespHandler),
                (r"/api/text-resp", TextResponseHanler),
                (r"/api/html-resp", HtmlResponseHanler),
                (r"/api/file-resp", FileResponseHanler),
            ]
        )
