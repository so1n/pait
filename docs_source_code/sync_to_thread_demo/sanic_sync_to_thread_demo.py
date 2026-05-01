from sanic import Sanic
from sanic.response import json

from pait.app.sanic import pait
from pait.field import Json

app = Sanic("sync_to_thread_demo")


def sync_heavy_task(data: str) -> str:
    """Simulate a slow synchronous task, such as a database query or file processing."""
    import time

    time.sleep(0.1)  # Simulate slow work.
    return f"Processed: {data}"


@app.route("/api/sync", methods=["POST"])
@pait(sync_to_thread=True)
def sync_route(data: str = Json.i(description="Data to process")):
    """Synchronous route function using sync_to_thread."""
    result = sync_heavy_task(data)
    return json({"result": result, "message": "Synchronous function executed in the thread pool"})


@app.route("/api/async", methods=["POST"])
@pait()
async def async_route(data: str = Json.i(description="Data to process")):
    """Regular async route function."""
    # In an async environment, synchronous work blocks the event loop.
    result = sync_heavy_task(data)
    return json({"result": result, "message": "Async function executed synchronous work directly"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
