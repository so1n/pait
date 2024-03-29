import json

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler


class DemoHandler(RequestHandler):
    def post(self) -> None:
        request_dict = json.loads(self.request.body.decode())
        uid_str: str = request_dict.get("uid", "")
        username: str = request_dict.get("username", "")

        uid = int(uid_str)  # Don't think about type conversion exceptions for now
        if not (10 < uid < 1000):
            raise ValueError("invalid uid")
        if not (2 <= len(username) <= 4):
            raise ValueError("invalid name")
        # get the corresponding value and return it
        self.write({"uid": uid, "username": username})


app: Application = Application([(r"/api", DemoHandler)])


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
