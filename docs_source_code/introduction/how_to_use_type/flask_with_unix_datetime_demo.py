import datetime
from typing import Callable, Generator, Union

from flask import Flask, Response, jsonify

from pait import field
from pait._pydanitc_adapter import is_v1
from pait.app.flask import pait

if is_v1:

    class UnixDatetime(datetime.datetime):
        @classmethod
        def __get_validators__(cls) -> Generator[Callable, None, None]:
            yield cls.validate

        @classmethod
        def validate(cls, v: Union[int, str]) -> datetime.datetime:
            if isinstance(v, str):
                v = int(v)
            return datetime.datetime.fromtimestamp(v)

else:
    from pydantic import BeforeValidator
    from typing_extensions import Annotated

    def validate(v: Union[int, str]) -> datetime.datetime:
        if isinstance(v, str):
            v = int(v)
        return datetime.datetime.fromtimestamp(v)

    UnixDatetime = Annotated[datetime.datetime, BeforeValidator(validate)]  # type: ignore


@pait()
def demo(timestamp: UnixDatetime = field.Query.i()) -> Response:
    return jsonify({"time": timestamp.isoformat()})


app = Flask("demo")
app.add_url_rule("/api/demo", "demo", demo, methods=["GET"])


if __name__ == "__main__":
    app.run(port=8000)
